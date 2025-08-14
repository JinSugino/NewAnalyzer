import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from services.chart_service import ChartService


class AnalysisService:
    """価格データから統計量や相関を算出し、表/ヒートマップを生成するサービス"""

    def __init__(self) -> None:
        self.chart_service = ChartService()
        self.data_dir = self.chart_service.data_dir

    # ---------- ファイル/データ取得 ----------
    def list_csv_files(self) -> List[str]:
        if not os.path.exists(self.data_dir):
            return []
        return [f for f in os.listdir(self.data_dir) if f.endswith(".csv")]

    def _filename_to_ticker(self, filename: str) -> str:
        return filename.replace(".csv", "")

    def load_close_series(self, filename: str) -> pd.Series:
        df = self.chart_service.load_csv_data(filename)
        s = df.set_index("Date")["Close"].sort_index().astype(float)
        s.name = self._filename_to_ticker(filename)
        return s

    def load_all_close_series(self, filenames: Optional[List[str]] = None) -> pd.DataFrame:
        files = filenames if filenames else self.list_csv_files()
        series_list: List[pd.Series] = []
        for f in files:
            try:
                series_list.append(self.load_close_series(f))
            except Exception:
                # 壊れたファイルはスキップ
                continue
        if not series_list:
            raise ValueError("有効なCSVがありません")
        df_close = pd.concat(series_list, axis=1, join="inner").sort_index()
        return df_close

    # ---------- 指標計算 ----------
    def compute_returns(self, prices: pd.DataFrame, method: str = "simple") -> pd.DataFrame:
        if method == "log":
            rets = np.log(prices / prices.shift(1))
        else:
            rets = prices.pct_change()
        rets = rets.dropna(how="all")
        return rets

    def compute_summary(
        self,
        filenames: Optional[List[str]] = None,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252,
        method: str = "simple",
    ) -> pd.DataFrame:
        prices = self.load_all_close_series(filenames)
        rets = self.compute_returns(prices, method=method)

        # 日次統計
        mean_daily = rets.mean()
        vol_daily = rets.std()
        sharpe_daily = (mean_daily - risk_free_rate / periods_per_year) / vol_daily.replace(0, np.nan)

        # 年率換算
        mean_annual = mean_daily * periods_per_year
        vol_annual = vol_daily * np.sqrt(periods_per_year)
        sharpe_annual = (mean_annual - risk_free_rate) / vol_annual.replace(0, np.nan)

        summary = pd.DataFrame(
            {
                "ticker": mean_daily.index,
                "mean_return_daily": mean_daily.values,
                "volatility_daily": vol_daily.values,
                "sharpe_daily": sharpe_daily.values,
                "mean_return_annual": mean_annual.values,
                "volatility_annual": vol_annual.values,
                "sharpe_annual": sharpe_annual.values,
                "observations": rets.count().values,
            }
        )
        # 見やすさのためソート（年率シャープ降順）
        summary = summary.sort_values("sharpe_annual", ascending=False).reset_index(drop=True)
        return summary

    def compute_correlation(self, filenames: Optional[List[str]] = None, method: str = "simple") -> pd.DataFrame:
        prices = self.load_all_close_series(filenames)
        rets = self.compute_returns(prices, method=method)
        corr = rets.corr()
        return corr

    def _find_correlated_groups(self, corr: pd.DataFrame, threshold: float = 0.9) -> List[List[str]]:
        """閾値を超える相関を持つ資産グループを見つける"""
        tickers = list(corr.columns)
        n = len(tickers)
        visited = set()
        groups = []
        
        for i in range(n):
            if tickers[i] in visited:
                continue
                
            # 新しいグループを開始
            group = [tickers[i]]
            visited.add(tickers[i])
            
            # 他の資産との相関をチェック
            for j in range(i + 1, n):
                if tickers[j] in visited:
                    continue
                    
                # グループ内の全ての資産との相関をチェック
                is_correlated = True
                for member in group:
                    if abs(corr.loc[member, tickers[j]]) < threshold:
                        is_correlated = False
                        break
                
                if is_correlated:
                    group.append(tickers[j])
                    visited.add(tickers[j])
            
            if len(group) > 1:  # 2つ以上の資産が相関している場合のみ
                groups.append(group)
        
        return groups

    def _create_representative_asset(self, prices: pd.DataFrame, group: List[str], method: str = "mean") -> pd.Series:
        """相関グループの代表資産を作成"""
        group_prices = prices[group]
        
        if method == "mean":
            # 価格の平均を取る
            representative = group_prices.mean(axis=1)
        elif method == "median":
            # 価格の中央値を取る
            representative = group_prices.median(axis=1)
        elif method == "first":
            # 最初の資産を代表とする
            representative = group_prices.iloc[:, 0]
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # 代表資産の名前を作成
        if len(group) <= 3:
            name = "+".join(group)
        else:
            name = f"{group[0]}+{len(group)-1}others"
        
        representative.name = name
        return representative

    def consolidate_correlated_assets(
        self, 
        filenames: Optional[List[str]] = None, 
        method: str = "simple",
        correlation_threshold: float = 0.9,
        consolidation_method: str = "mean"
    ) -> Dict:
        """相関の高い資産グループを代表資産に統合"""
        prices = self.load_all_close_series(filenames)
        rets = self.compute_returns(prices, method=method)
        corr = rets.corr()
        
        # 相関グループを見つける
        groups = self._find_correlated_groups(corr, correlation_threshold)
        
        # 統合後の価格データを作成
        consolidated_prices = prices.copy()
        consolidated_rets = rets.copy()
        
        # 各グループを代表資産に置き換え
        for group in groups:
            # 代表資産を作成
            representative = self._create_representative_asset(prices, group, consolidation_method)
            
            # グループの最初の資産を代表資産で置き換え
            first_asset = group[0]
            consolidated_prices[first_asset] = representative
            
            # 他の資産を削除
            for asset in group[1:]:
                if asset in consolidated_prices.columns:
                    consolidated_prices = consolidated_prices.drop(columns=[asset])
                    consolidated_rets = consolidated_rets.drop(columns=[asset])
        
        # 統合後の相関行列を計算
        consolidated_corr = consolidated_rets.corr()
        
        return {
            "original_correlation": corr,
            "consolidated_correlation": consolidated_corr,
            "groups": groups,
            "consolidated_prices": consolidated_prices,
            "consolidated_returns": consolidated_rets
        }

    # ---------- 可視化（Plotly） ----------
    def create_summary_table_figure(self, summary: pd.DataFrame, title: str = "統計量サマリ") -> Dict:
        # 表示桁の整形
        df = summary.copy()
        for col in ["mean_return_daily", "volatility_daily", "sharpe_daily", "mean_return_annual", "volatility_annual", "sharpe_annual"]:
            df[col] = df[col].astype(float)
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=[
                            "Ticker",
                            "Mean(daily)",
                            "Vol(daily)",
                            "Sharpe(daily)",
                            "Mean(annual)",
                            "Vol(annual)",
                            "Sharpe(annual)",
                            "Obs",
                        ],
                        fill_color="#f5f5f5",
                        align="center",
                    ),
                    cells=dict(
                        values=[
                            df["ticker"],
                            (df["mean_return_daily"] * 100).map(lambda x: f"{x:.2f}%"),
                            (df["volatility_daily"] * 100).map(lambda x: f"{x:.2f}%"),
                            df["sharpe_daily"].map(lambda x: f"{x:.2f}"),
                            (df["mean_return_annual"] * 100).map(lambda x: f"{x:.2f}%"),
                            (df["volatility_annual"] * 100).map(lambda x: f"{x:.2f}%"),
                            df["sharpe_annual"].map(lambda x: f"{x:.2f}"),
                            df["observations"],
                        ],
                        align="center",
                    ),
                )
            ]
        )
        fig.update_layout(title=title, template="plotly_white", height=600)
        return fig.to_dict()

    def create_correlation_heatmap_figure(self, corr: pd.DataFrame, title: str = "相関係数ヒートマップ") -> Dict:
        # 並び替え（クラスタ順等は未実装。単純にラベル順）
        tickers = list(corr.columns)
        z = corr.values
        fig = go.Figure(
            data=go.Heatmap(z=z, x=tickers, y=tickers, colorscale="RdBu", zmin=-1, zmax=1, colorbar=dict(title="Corr"))
        )
        fig.update_layout(title=title, template="plotly_white", height=700)
        return fig.to_dict()

    # ---------- 高レベルAPI ----------
    def get_summary(self, tickers: Optional[List[str]] = None, risk_free_rate: float = 0.0, periods_per_year: int = 252, method: str = "simple") -> Dict:
        filenames = None
        if tickers:
            all_files = self.list_csv_files()
            filenames = [f for f in all_files if self._filename_to_ticker(f) in set(tickers)]
        summary_df = self.compute_summary(filenames, risk_free_rate=risk_free_rate, periods_per_year=periods_per_year, method=method)
        table_fig = self.create_summary_table_figure(summary_df)
        return {"summary": summary_df.to_dict(orient="records"), "table": table_fig}

    def get_correlation(self, tickers: Optional[List[str]] = None, method: str = "simple") -> Dict:
        filenames = None
        if tickers:
            all_files = self.list_csv_files()
            filenames = [f for f in all_files if self._filename_to_ticker(f) in set(tickers)]
        corr_df = self.compute_correlation(filenames, method=method)
        heatmap_fig = self.create_correlation_heatmap_figure(corr_df)
        return {"matrix": corr_df.round(4).to_dict(), "heatmap": heatmap_fig}

    def get_consolidated_correlation(
        self, 
        tickers: Optional[List[str]] = None, 
        method: str = "simple",
        correlation_threshold: float = 0.9,
        consolidation_method: str = "mean"
    ) -> Dict:
        """相関の高い資産を統合した相関分析"""
        filenames = None
        if tickers:
            all_files = self.list_csv_files()
            filenames = [f for f in all_files if self._filename_to_ticker(f) in set(tickers)]
        
        result = self.consolidate_correlated_assets(
            filenames, 
            method=method,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method
        )
        
        # 統合前後のヒートマップを作成
        original_heatmap = self.create_correlation_heatmap_figure(
            result["original_correlation"], 
            title=f"統合前相関ヒートマップ (閾値: {correlation_threshold})"
        )
        consolidated_heatmap = self.create_correlation_heatmap_figure(
            result["consolidated_correlation"], 
            title=f"統合後相関ヒートマップ (統合方法: {consolidation_method})"
        )
        
        return {
            "original_matrix": result["original_correlation"].round(4).to_dict(),
            "consolidated_matrix": result["consolidated_correlation"].round(4).to_dict(),
            "groups": result["groups"],
            "original_heatmap": original_heatmap,
            "consolidated_heatmap": consolidated_heatmap,
            "consolidation_info": {
                "threshold": correlation_threshold,
                "method": consolidation_method,
                "original_assets": len(result["original_correlation"]),
                "consolidated_assets": len(result["consolidated_correlation"])
            }
        }
