import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from services.chart_service import ChartService
from services.analysis_service import AnalysisService


class PortfolioService:
    """ポートフォリオ最適化ユースケースのためのユーティリティ

    - 価格CSVからμ（期待リターン）とΣ（共分散）を推定
    - 実行可能ポートフォリオ集合の可視化（サンプリング）
    - 効率的フロンティア：
      - ショート可: 解析解 w = λ Σ⁻¹ 1 + γ Σ⁻¹ μ（A,B,C,D から λ,γ を閉形式で算出）
      - ショート禁止等の制約: SLSQP で QP を数値的に解く
    """

    def __init__(self) -> None:
        self.chart_service = ChartService()
        self.analysis_service = AnalysisService()
        self.data_dir = self.chart_service.data_dir

    # ---------- データ読み込み ----------
    def list_csv_files(self) -> List[str]:
        if not os.path.exists(self.data_dir):
            return []
        # USDJPY.csvを除外し、株価データのみを取得
        return [f for f in os.listdir(self.data_dir) if f.endswith(".csv") and f != "USDJPY.csv"]

    def _filename_to_ticker(self, filename: str) -> str:
        return filename.replace(".csv", "")

    def load_close_prices(self, filenames: Optional[List[str]] = None, currency: str = "USD") -> pd.DataFrame:
        files = filenames if filenames else self.list_csv_files()
        series_list: List[pd.Series] = []
        for f in files:
            try:
                # 通貨換算に対応したファイルパスを取得
                from services.currency_service import CurrencyService
                currency_service = CurrencyService()
                file_path = currency_service.get_analysis_file_path(f, currency)
                
                # ファイルを読み込み
                df = pd.read_csv(file_path)
                
                # 特殊なCSV構造に対応（最初の2行をスキップしてDateカラムを設定）
                if 'Date' not in df.columns and len(df.columns) >= 6:
                    df = df.iloc[2:].reset_index(drop=True)
                    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                    
                    # 空のDate行を削除
                    df = df.dropna(subset=['Date'])
                    df = df[df['Date'] != '']
                
                # 数値列を数値型に変換
                for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 欠損値を削除
                df = df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
                
                df['Date'] = pd.to_datetime(df['Date'])
                
                s = df.set_index("Date")["Close"].astype(float)
                s.name = self._filename_to_ticker(f)
                series_list.append(s)
            except Exception as e:
                print(f"Error loading {f}: {e}")
                continue
        if not series_list:
            raise ValueError("有効なCSVがありません")
        prices = pd.concat(series_list, axis=1, join="inner").sort_index()
        return prices

    # ---------- 推定（μ, Σ） ----------
    def estimate_mu_sigma(
        self,
        filenames: Optional[List[str]] = None,
        *,
        method: str = "simple",
        annualize: bool = True,
        periods_per_year: int = 252,
        consolidate_correlated: bool = False,
        correlation_threshold: float = 0.9,
        consolidation_method: str = "mean",
        currency: str = "USD",
    ) -> Tuple[pd.Series, pd.DataFrame]:
        if consolidate_correlated:
            # 相関統合を先に実行
            result = self.analysis_service.consolidate_correlated_assets(
                filenames,
                method=method,
                correlation_threshold=correlation_threshold,
                consolidation_method=consolidation_method,
                currency=currency
            )
            prices = result["consolidated_prices"]
        else:
            prices = self.load_close_prices(filenames, currency=currency)
        
        if method == "log":
            rets = np.log(prices / prices.shift(1))
        else:
            rets = prices.pct_change()
        rets = rets.dropna(how="any")
        mu_daily = rets.mean()
        sigma_daily = rets.cov()
        if annualize:
            mu = mu_daily * periods_per_year
            Sigma = sigma_daily * periods_per_year
        else:
            mu = mu_daily
            Sigma = sigma_daily
        return mu, Sigma

    # ---------- 解析的フロンティア（ショート可） ----------
    def efficient_frontier_analytic(self, mu: pd.Series, Sigma: pd.DataFrame, return_targets: np.ndarray) -> Dict[str, np.ndarray]:
        mu_vec = mu.values.astype(float)
        Sigma_val = Sigma.values.astype(float)
        inv_Sigma = np.linalg.inv(Sigma_val)
        ones = np.ones(len(mu_vec))

        A = float(ones @ inv_Sigma @ ones)
        B = float(ones @ inv_Sigma @ mu_vec)
        C = float(mu_vec @ inv_Sigma @ mu_vec)
        D = A * C - B ** 2
        if D <= 0:
            raise ValueError("Δ<=0 でフロンティアの解析計算ができません")

        a = 1.0 / A
        b = A / D
        h = B / A

        targets = np.asarray(return_targets, dtype=float)
        risks: List[float] = []
        weights_list: List[np.ndarray] = []
        for r_target in targets:
            sigma = float(np.sqrt(max(a + b * (r_target - h) ** 2, 0.0)))
            risks.append(sigma)
            lambda_ = (C - B * r_target) / D
            gamma = (A * r_target - B) / D
            w = lambda_ * (inv_Sigma @ ones) + gamma * (inv_Sigma @ mu_vec)
            weights_list.append(w)

        return {
            "target_returns": targets,
            "risks": np.array(risks),
            "weights_list": weights_list,
            "coeffs": {"A": A, "B": B, "C": C, "D": D, "a": a, "b": b, "h": h},
        }



    # ---------- 実行可能集合（サンプリング） ----------
    def sample_feasible_portfolios(
        self,
        mu: pd.Series,
        Sigma: pd.DataFrame,
        *,
        allow_short: bool = False,
        num_samples: int = 2000,
        max_leverage: float = 2.0,
    ) -> pd.DataFrame:
        n = len(mu)
        records: List[Tuple[float, float]] = []
        weights: List[np.ndarray] = []
        rng = np.random.default_rng(42)
        if not allow_short:
            for _ in range(num_samples):
                w = rng.dirichlet(np.ones(n))
                ret = float(w @ mu.values)
                var = float(w.T @ Sigma.values @ w)
                records.append((np.sqrt(max(var, 0.0)), ret))
                weights.append(w)
        else:
            count = 0
            while count < num_samples:
                w = rng.normal(size=n)
                if np.isclose(w.sum(), 0):
                    continue
                w = w / w.sum()
                if np.sum(np.abs(w)) > max_leverage:
                    continue
                ret = float(w @ mu.values)
                var = float(w.T @ Sigma.values @ w)
                records.append((np.sqrt(max(var, 0.0)), ret))
                weights.append(w)
                count += 1
        df = pd.DataFrame(records, columns=["risk", "return"]).assign(weights=weights)
        return df

    # ---------- ウェイト選択ユーティリティ ----------
    def _tangency_weights(self, mu: pd.Series, Sigma: pd.DataFrame, r_f: float) -> np.ndarray:
        inv_Sigma = np.linalg.inv(Sigma.values)
        one = np.ones((len(mu), 1))
        excess = (mu.values.reshape(-1, 1) - r_f * one)
        w = inv_Sigma @ excess
        w = (w / (one.T @ w)).flatten()
        return w

    def _min_variance_weights(self, Sigma: pd.DataFrame) -> np.ndarray:
        inv_Sigma = np.linalg.inv(Sigma.values)
        one = np.ones((Sigma.shape[0], 1))
        w = inv_Sigma @ one
        w = (w / (one.T @ w)).flatten()
        return w

    def _select_composition_weights(
        self,
        *,
        mode: str,
        mu: pd.Series,
        Sigma: pd.DataFrame,
        r_f: float,
        allow_short: bool,
        ef_weights: Optional[List[np.ndarray]],
        ef_targets: Optional[np.ndarray],
        ef_risks: Optional[np.ndarray],
        sampled: Optional[pd.DataFrame],
        composition_target_return: Optional[float],
    ) -> np.ndarray:
        mode = (mode or "tangency").lower()
        
        # 効率的フロンティアから選択（ショート可/不可に関係なく）
        if ef_weights is not None and ef_targets is not None and ef_risks is not None and len(ef_weights) > 0:
            if mode == "tangency" and r_f is not None:
                # シャープレシオが最大のフロンティア上の点を選択
                sharpe_ratios = (ef_targets - r_f) / ef_risks
                idx = int(np.argmax(sharpe_ratios))
                w = ef_weights[idx]
            elif mode == "min_variance":
                # リスク最小のフロンティア上の点を選択
                idx = int(np.argmin(ef_risks))
                w = ef_weights[idx]
            elif mode == "target_return" and composition_target_return is not None:
                # 目標リターンに最も近いフロンティア上の点を選択
                idx = int(np.argmin(np.abs(ef_targets - composition_target_return)))
                w = ef_weights[idx]
            else:
                # フロンティアの中間点を選択
                w = ef_weights[len(ef_weights) // 2]
            
            # ショート禁止の場合、負のウェイトを0に修正
            if not allow_short:
                w = np.maximum(w, 0.0)
                # 正規化して合計を1に
                if w.sum() > 0:
                    w = w / w.sum()
            return w
        
        # フォールバック: ショート可の場合は解析解、ショート禁止の場合はサンプルから選択
        if allow_short:
            if mode == "tangency" and r_f is not None:
                return self._tangency_weights(mu, Sigma, r_f)
            if mode == "min_variance":
                return self._min_variance_weights(Sigma)
            # fallback: equal weight
            return np.ones(len(mu)) / len(mu)
        else:
            # 制約あり: サンプルから選択
            if sampled is None or len(sampled) == 0:
                return np.ones(len(mu)) / len(mu)
            df = sampled.copy()
            if mode == "tangency" and r_f is not None:
                df = df.assign(sharpe=(df["return"] - r_f) / df["risk"].replace(0, np.nan))
                idx = int(df["sharpe"].idxmax())
            elif mode == "min_variance":
                idx = int(df["risk"].idxmin())
            elif mode == "target_return" and composition_target_return is not None:
                idx = int((df["return"] - composition_target_return).abs().idxmin())
            else:
                # mid by return
                df = df.sort_values("return")
                idx = df.index[len(df) // 2]
            # weights列に保存済み
            w = df.loc[idx, "weights"]
            # ショート禁止の場合、負のウェイトを0に修正
            if not allow_short:
                w = np.maximum(w, 0.0)
                # 正規化して合計を1に
                if w.sum() > 0:
                    w = w / w.sum()
            return np.array(w)

    # ---------- 図表生成 ----------
    def create_feasible_set_figure(
        self,
        mu: pd.Series,
        Sigma: pd.DataFrame,
        *,
        r_f: float = 0.0,
        allow_short: bool = True,
        target_return_min: Optional[float] = None,
        target_return_max: Optional[float] = None,
        num_frontier_points: int = 50,
        num_samples: int = 2000,
        max_leverage: float = 2.0,
        composition_mode: str = "tangency",
        composition_target_return: Optional[float] = None,
    ) -> Dict:
        tickers = list(mu.index)
        # 可視参考用のサンプル雲
        sampled = self.sample_feasible_portfolios(mu, Sigma, allow_short=allow_short, num_samples=num_samples, max_leverage=max_leverage)

        # 目標リターン範囲
        if target_return_min is None or target_return_max is None:
            if len(sampled):
                target_return_min = float(np.percentile(sampled["return"], 5))
                target_return_max = float(np.percentile(sampled["return"], 95))
            else:
                target_return_min = float(mu.min()) * 0.5
                target_return_max = float(mu.max()) * 1.5

        ef_weights_list: Optional[List[np.ndarray]] = None
        ef_targets_arr: Optional[np.ndarray] = None
        # 常に解析解を使用（ショート可/不可に関係なく）
        targets = np.linspace(target_return_min, target_return_max, num_frontier_points)
        ef = self.efficient_frontier_analytic(mu, Sigma, return_targets=targets)
        frontier_x = ef["risks"].tolist()
        frontier_y = ef["target_returns"].tolist()
        ef_weights_list = ef["weights_list"]
        ef_targets_arr = ef["target_returns"]

        # 構成ウェイトを選択
        w_sel = self._select_composition_weights(
            mode=composition_mode,
            mu=mu,
            Sigma=Sigma,
            r_f=r_f,
            allow_short=allow_short,
            ef_weights=ef_weights_list,
            ef_targets=ef_targets_arr,
            ef_risks=ef["risks"],
            sampled=sampled,
            composition_target_return=composition_target_return,
        )

        # 図: 上段に集合, 下段左右に円グラフと表
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"colspan": 2}, None], [{"type": "domain"}, {"type": "table"}]],
            row_heights=[0.68, 0.32],
            vertical_spacing=0.08,
            horizontal_spacing=0.08,
            subplot_titles=("Feasible Set & Efficient Frontier", "Composition (%)", "Weights Table"),
        )

        # 上段: サンプル雲、フロンティア、資産点、CML
        if len(sampled):
            fig.add_scatter(x=sampled["risk"], y=sampled["return"], mode="markers", name="Feasible", marker=dict(size=4, color="rgba(0,0,0,0.22)"), row=1, col=1)
        fig.add_scatter(x=frontier_x, y=frontier_y, mode="lines", name="Frontier", line=dict(color="#EF5350", width=2), row=1, col=1)
        asset_sigma = np.sqrt(np.diag(Sigma.values))
        asset_ret = mu.values
        fig.add_scatter(x=asset_sigma, y=asset_ret, mode="markers+text", text=tickers, textposition="top center", name="Assets (100%)", marker=dict(size=9, color="#42A5F5"), row=1, col=1)
        if r_f is not None:
            # フロンティアからタンジェンシーポートフォリオを計算
            if ef_weights_list is not None and ef_targets_arr is not None and len(ef_weights_list) > 0:
                # シャープレシオが最大のフロンティア上の点を選択
                sharpe_ratios = (ef_targets_arr - r_f) / ef["risks"]
                idx = int(np.argmax(sharpe_ratios))
                w_tan = ef_weights_list[idx]
                
                # ショート禁止の場合、負のウェイトを0に修正
                if not allow_short:
                    w_tan = np.maximum(w_tan, 0.0)
                    # 正規化して合計を1に
                    if w_tan.sum() > 0:
                        w_tan = w_tan / w_tan.sum()
                
                ret_tan = float(w_tan @ mu.values)
                risk_tan = float(np.sqrt(max(w_tan.T @ Sigma.values @ w_tan, 0.0)))
                slope = (ret_tan - r_f) / max(risk_tan, 1e-12)
                x_cml = np.linspace(0.0, max(frontier_x) if len(frontier_x) else risk_tan * 1.5, 50)
                y_cml = r_f + slope * x_cml
                fig.add_scatter(x=x_cml, y=y_cml, mode="lines", name="CML", line=dict(color="#4CAF50", width=2, dash="dot"), row=1, col=1)
                fig.add_scatter(x=[risk_tan], y=[ret_tan], mode="markers", name="Tangency", marker=dict(size=10, color="#FF9800", symbol="star"), row=1, col=1)
                # Tangencyでショートの資産にXマーカーを重ねる（ショート可の場合のみ）
                if allow_short:
                    short_idx = [i for i, ww in enumerate(w_tan) if ww < 0]
                    if short_idx:
                        fig.add_scatter(
                            x=asset_sigma[short_idx],
                            y=asset_ret[short_idx],
                            mode="markers",
                            name="Short in Tangency",
                            marker=dict(symbol="x", size=14, color="#EF5350", line=dict(width=2, color="#EF5350")),
                            showlegend=True,
                            row=1, col=1,
                        )

        fig.update_xaxes(title_text="Risk (σ)", row=1, col=1)
        fig.update_yaxes(title_text="Expected Return (μ)", row=1, col=1)

        # 下段: 円グラフ（ショートありは |w| を使用）
        pie_vals = np.abs(w_sel)
        if pie_vals.sum() <= 0:
            pie_vals = np.ones_like(pie_vals)
        colors = ["#26A69A" if w >= 0 else "#EF5350" for w in w_sel]
        fig.add_trace(
            go.Pie(labels=tickers, values=(pie_vals * 100.0), hole=0.35, sort=False,
                   textinfo="percent+label", hovertemplate="%{label}: %{value:.2f}%<extra></extra>", marker=dict(colors=colors), name="Weights"),
            row=2, col=1
        )

        # 下段: 表（符号付きウェイト% と Short?）
        weight_pct = (w_sel * 100.0)
        short_flags = ["Yes" if w < 0 else "No" for w in w_sel]
        fig.add_trace(
            go.Table(
                header=dict(values=["Ticker", "Weight %", "Short?"], fill_color="#f5f5f5", align="center"),
                cells=dict(values=[tickers, [f"{v:+.2f}%" for v in weight_pct], short_flags], align="center")
            ),
            row=2, col=2
        )

        fig.update_layout(template="plotly_white", height=760)
        return fig.to_dict()

    # ---------- ハイレベル ----------
    def get_portfolio_inputs(
        self, 
        filenames: Optional[List[str]] = None, 
        *, 
        method: str = "simple", 
        annualize: bool = True, 
        periods_per_year: int = 252,
        consolidate_correlated: bool = False,
        correlation_threshold: float = 0.9,
        consolidation_method: str = "mean"
    ) -> Dict:
        mu, Sigma = self.estimate_mu_sigma(
            filenames, 
            method=method, 
            annualize=annualize, 
            periods_per_year=periods_per_year,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method
        )
        return {
            "tickers": list(mu.index),
            "mu": mu.to_dict(),
            "Sigma": pd.DataFrame(Sigma, index=mu.index, columns=mu.index).to_dict(),
        }

    def get_feasible_set_figure(
        self,
        filenames: Optional[List[str]] = None,
        *,
        method: str = "simple",
        annualize: bool = True,
        periods_per_year: int = 252,
        r_f: float = 0.0,
        allow_short: bool = True,
        target_return_min: Optional[float] = None,
        target_return_max: Optional[float] = None,
        num_frontier_points: int = 50,
        num_samples: int = 2000,
        max_leverage: float = 2.0,
        composition_mode: str = "tangency",
        composition_target_return: Optional[float] = None,
        consolidate_correlated: bool = False,
        correlation_threshold: float = 0.9,
        consolidation_method: str = "mean",
    ) -> Dict:
        mu, Sigma = self.estimate_mu_sigma(
            filenames, 
            method=method, 
            annualize=annualize, 
            periods_per_year=periods_per_year,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method
        )
        fig = self.create_feasible_set_figure(
            mu, Sigma,
            r_f=r_f,
            allow_short=allow_short,
            target_return_min=target_return_min,
            target_return_max=target_return_max,
            num_frontier_points=num_frontier_points,
            num_samples=num_samples,
            max_leverage=max_leverage,
            composition_mode=composition_mode,
            composition_target_return=composition_target_return,
        )
        return {"mu": mu.to_dict(), "Sigma": pd.DataFrame(Sigma, index=mu.index, columns=mu.index).to_dict(), "figure": fig}

    def get_optimization_figure(
        self,
        filenames: Optional[List[str]] = None,
        *,
        method: str = "simple",
        annualize: bool = True,
        periods_per_year: int = 252,
        r_f: float = 0.0,
        allow_short: bool = True,
        num_frontier_points: int = 50,
        num_samples: int = 2000,
        max_leverage: float = 2.0,
        consolidate_correlated: bool = False,
        correlation_threshold: float = 0.9,
        consolidation_method: str = "mean",
        optimization_method: str = "sharpe",
        target_return: Optional[float] = None,
        target_risk: Optional[float] = None,
        risk_tolerance: float = 1.0,
        max_weight: float = 1.0,
        min_weight: float = 0.0,
        currency: str = "USD",
    ) -> Dict:
        mu, Sigma = self.estimate_mu_sigma(
            filenames, 
            method=method, 
            annualize=annualize, 
            periods_per_year=periods_per_year,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method,
            currency=currency
        )
        
        # 最適化方法に応じて適切なパラメータを設定
        if optimization_method == "sharpe":
            composition_mode = "tangency"
            composition_target_return = None
        elif optimization_method == "min_variance":
            composition_mode = "min_variance"
            composition_target_return = None
        elif optimization_method == "max_return":
            composition_mode = "max_return"
            composition_target_return = None
        else:
            composition_mode = "tangency"
            composition_target_return = None
        
        fig = self.create_feasible_set_figure(
            mu, Sigma,
            r_f=r_f,
            allow_short=allow_short,
            target_return_min=None,
            target_return_max=None,
            num_frontier_points=num_frontier_points,
            num_samples=num_samples,
            max_leverage=max_leverage,
            composition_mode=composition_mode,
            composition_target_return=composition_target_return,
        )
        return {"mu": mu.to_dict(), "Sigma": pd.DataFrame(Sigma, index=mu.index, columns=mu.index).to_dict(), "figure": fig}

    def get_efficient_frontier_figure(
        self,
        filenames: Optional[List[str]] = None,
        *,
        method: str = "simple",
        annualize: bool = True,
        periods_per_year: int = 252,
        r_f: float = 0.0,
        allow_short: bool = True,
        num_frontier_points: int = 50,
        num_samples: int = 2000,
        max_leverage: float = 2.0,
        consolidate_correlated: bool = False,
        correlation_threshold: float = 0.9,
        consolidation_method: str = "mean",
        optimization_method: str = "sharpe",
        target_return: Optional[float] = None,
        target_risk: Optional[float] = None,
        risk_tolerance: float = 1.0,
        max_weight: float = 1.0,
        min_weight: float = 0.0,
        currency: str = "USD",
    ) -> Dict:
        mu, Sigma = self.estimate_mu_sigma(
            filenames, 
            method=method, 
            annualize=annualize, 
            periods_per_year=periods_per_year,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method,
            currency=currency
        )
        
        # 効率的フロンティアの表示
        fig = self.create_feasible_set_figure(
            mu, Sigma,
            r_f=r_f,
            allow_short=allow_short,
            target_return_min=None,
            target_return_max=None,
            num_frontier_points=num_frontier_points,
            num_samples=num_samples,
            max_leverage=max_leverage,
            composition_mode="efficient_frontier",
            composition_target_return=None,
        )
        return {"mu": mu.to_dict(), "Sigma": pd.DataFrame(Sigma, index=mu.index, columns=mu.index).to_dict(), "figure": fig}
