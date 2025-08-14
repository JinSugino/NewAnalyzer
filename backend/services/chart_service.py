import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from typing import Dict, Any, Optional, List
import os

class ChartService:
    """ローソク足チャートと出来高折れ線グラフを生成するサービス"""
    
    def __init__(self):
        self.data_dir = "data"
    
    def load_csv_data(self, filename: str) -> pd.DataFrame:
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        raw = pd.read_csv(file_path, header=None, dtype=str, engine="python")
        if raw.empty:
            raise ValueError("CSVが空です")
        max_cols = 6
        if raw.shape[1] < max_cols:
            for _ in range(max_cols - raw.shape[1]):
                raw[raw.shape[1]] = None
        raw = raw.iloc[:, :max_cols]
        raw.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        tmp = raw.copy()
        tmp['Date'] = pd.to_datetime(tmp['Date'], errors='coerce')
        tmp = tmp.dropna(subset=['Date'])
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            tmp[col] = pd.to_numeric(tmp[col], errors='coerce')
        tmp = tmp.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
        tmp = tmp.sort_values('Date').reset_index(drop=True)
        if tmp.empty:
            raise ValueError("有効なデータ行が存在しません。CSVの形式をご確認ください。")
        return tmp

    def _parse_annotation_dates(self, df: pd.DataFrame, annotate_dates: Optional[List[str]], mark_month_start: bool) -> List[pd.Timestamp]:
        marks: List[pd.Timestamp] = []
        if annotate_dates:
            for s in annotate_dates:
                if not s:
                    continue
                d = pd.to_datetime(s, errors='coerce')
                if pd.isna(d):
                    continue
                marks.append(pd.Timestamp(d.date()))
        if mark_month_start:
            df2 = df.copy()
            df2['date_only'] = df2['Date'].dt.date
            df2['year_month'] = df2['Date'].dt.to_period('M')
            firsts = df2.groupby('year_month')['date_only'].min().tolist()
            marks.extend(pd.Timestamp(x) for x in firsts)
        if marks:
            min_d, max_d = df['Date'].min().normalize(), df['Date'].max().normalize()
            unique = []
            seen = set()
            for d in sorted(marks):
                if d < min_d or d > max_d:
                    continue
                if d in seen:
                    continue
                seen.add(d)
                unique.append(d)
            if len(unique) > 20:
                step = max(1, len(unique) // 20)
                unique = unique[::step]
            return unique
        return []

    def _add_date_annotations(self, fig: go.Figure, df: pd.DataFrame, marks: List[pd.Timestamp]) -> None:
        if not marks:
            return
        for d in marks:
            fig.add_shape(
                type='line', x0=d, x1=d, xref='x', y0=0, y1=1, yref='paper',
                line=dict(color='rgba(0,0,0,0.20)', width=1, dash='dot')
            )
            fig.add_annotation(
                x=d, y=1.02, xref='x', yref='paper', text=d.strftime('%Y-%m-%d'),
                showarrow=False, font=dict(size=10, color='#666'), xanchor='center', align='center'
            )

    def _apply_axis_ticks(self, fig: go.Figure, df: pd.DataFrame, *, axis_tick: str = "auto", axis_tick_format: Optional[str] = None, axis_tick_dates: Optional[List[str]] = None, bottom_row: int = 2) -> None:
        if axis_tick == "auto":
            if axis_tick_format:
                fig.update_xaxes(tickformat=axis_tick_format, row=bottom_row, col=1)
            return
        if axis_tick in {"day", "week", "month", "quarter", "year"}:
            mapping = {"day": "D1", "week": "W1", "month": "M1", "quarter": "M3", "year": "M12"}
            dtick = mapping[axis_tick]
            fig.update_xaxes(dtick=dtick, tickformat=axis_tick_format or "%Y-%m-%d", row=bottom_row, col=1)
            return
        if axis_tick == "array":
            if not axis_tick_dates:
                return
            ticks: List[pd.Timestamp] = []
            for s in axis_tick_dates:
                d = pd.to_datetime(s, errors='coerce')
                if pd.isna(d):
                    continue
                ticks.append(pd.Timestamp(d))
            if not ticks:
                return
            min_d, max_d = df['Date'].min(), df['Date'].max()
            ticks = [t for t in sorted(set(ticks)) if (t >= min_d and t <= max_d)]
            if not ticks:
                return
            ticktext = [t.strftime(axis_tick_format or "%Y-%m-%d") for t in ticks]
            fig.update_xaxes(tickmode='array', tickvals=ticks, ticktext=ticktext, row=bottom_row, col=1)
            return

    # --------- 指標計算ユーティリティ ---------
    def _compute_bb(self, close: pd.Series, window: int = 20, num_std: float = 2.0):
        ma = close.rolling(window=window, min_periods=1).mean()
        sd = close.rolling(window=window, min_periods=1).std(ddof=0)
        upper = ma + num_std * sd
        lower = ma - num_std * sd
        return ma, upper, lower

    def _compute_rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)

    def _compute_macd(self, close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        hist = macd - macd_signal
        return macd, macd_signal, hist

    def _compute_vwap(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        cum_pv = (close * volume).cumsum()
        cum_vol = volume.cumsum().replace(0, pd.NA)
        vwap = (cum_pv / cum_vol).fillna(method='ffill')
        return vwap

    def _max_drawdown(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        s_close = df.set_index('Date')['Close']
        cummax = s_close.cummax()
        drawdown = s_close / cummax - 1.0
        if drawdown.empty:
            return None
        trough_date = drawdown.idxmin()
        peak_date = s_close.loc[:trough_date].idxmax()
        mdd = float(drawdown.min())
        # 可視化用のY範囲
        mask = (df['Date'] >= peak_date) & (df['Date'] <= trough_date)
        if not mask.any():
            return None
        y0 = float(df.loc[mask, 'Low'].min())
        y1 = float(df.loc[mask, 'High'].max())
        return {
            'peak': peak_date,
            'trough': trough_date,
            'mdd': mdd,
            'y0': y0,
            'y1': y1,
        }

    # --------- チャート生成 ---------
    def _build_chart(
        self,
        df: pd.DataFrame,
        title: str,
        *,
        annotate_dates: Optional[List[str]] = None,
        mark_month_start: bool = False,
        axis_tick: str = "auto",
        axis_tick_format: Optional[str] = None,
        axis_tick_dates: Optional[List[str]] = None,
        show_ma: bool = True,
        ma_windows: Optional[List[int]] = None,
        show_bb: bool = False,
        bb_window: int = 20,
        bb_std: float = 2.0,
        show_rsi: bool = False,
        rsi_period: int = 14,
        show_macd: bool = False,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        show_vwap: bool = False,
        show_mdd: bool = False,
    ) -> Dict[str, Any]:
        include_rsi = show_rsi
        include_macd = show_macd
        rows_total = 2 + (1 if include_rsi else 0) + (1 if include_macd else 0)  # price + (rsi) + (macd) + volume
        row_price = 1
        row_rsi = 2 if include_rsi else None
        row_macd = (2 if include_macd and not include_rsi else (3 if include_macd and include_rsi else None))
        row_volume = rows_total
        row_heights: List[float] = [0.62]
        if include_rsi:
            row_heights.append(0.18)
        if include_macd:
            row_heights.append(0.18)
        row_heights.append(0.22)

        fig = make_subplots(
            rows=rows_total,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(title,) + (() if not include_rsi else ("RSI",)) + (() if not include_macd else ("MACD",)) + ("出来高",),
            row_heights=row_heights,
        )

        # Price panel
        fig.add_trace(
            go.Candlestick(
                x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="ローソク足", increasing_line_color='#26A69A', decreasing_line_color='#EF5350'
            ),
            row=row_price, col=1
        )

        # Moving Averages
        if show_ma:
            windows = ma_windows if ma_windows else [5, 25]
            palette = ['#FF9800', '#9C27B0', '#4CAF50', '#795548']
            for i, w in enumerate(windows):
                ma = df['Close'].rolling(window=w, min_periods=1).mean()
                fig.add_trace(
                    go.Scatter(x=df['Date'], y=ma, mode='lines', name=f"MA{w}", line=dict(color=palette[i % len(palette)], width=1)),
                    row=row_price, col=1
                )

        # Bollinger Bands
        if show_bb:
            ma, upper, lower = self._compute_bb(df['Close'], window=bb_window, num_std=bb_std)
            fig.add_trace(go.Scatter(x=df['Date'], y=upper, line=dict(color='rgba(33,150,243,0.6)', width=1), name='BB upper'), row=row_price, col=1)
            fig.add_trace(go.Scatter(x=df['Date'], y=lower, line=dict(color='rgba(33,150,243,0.6)', width=1), name='BB lower', fill='tonexty', fillcolor='rgba(33,150,243,0.10)'), row=row_price, col=1)
            fig.add_trace(go.Scatter(x=df['Date'], y=ma, line=dict(color='rgba(33,150,243,0.8)', width=1, dash='dot'), name='BB basis'), row=row_price, col=1)

        # VWAP
        if show_vwap:
            vwap = self._compute_vwap(df['Close'], df['Volume'])
            fig.add_trace(go.Scatter(x=df['Date'], y=vwap, mode='lines', name='VWAP', line=dict(color='#3F51B5', width=1.2)), row=row_price, col=1)

        # Max Drawdown highlight
        if show_mdd:
            mdd_info = self._max_drawdown(df)
            if mdd_info:
                peak = mdd_info['peak']
                trough = mdd_info['trough']
                y0, y1 = mdd_info['y0'], mdd_info['y1']
                fig.add_shape(
                    type='rect', x0=peak, x1=trough, xref='x', y0=y0, y1=y1, yref='y',
                    fillcolor='rgba(239,83,80,0.15)', line=dict(width=0)
                )
                fig.add_annotation(x=trough, y=df.loc[df['Date'] == trough, 'Close'].iloc[0],
                                   text=f"Max DD {mdd_info['mdd']:.1%}", showarrow=True,
                                   arrowhead=1, font=dict(color='#EF5350'))

        # RSI panel
        if include_rsi and row_rsi is not None:
            rsi = self._compute_rsi(df['Close'], period=rsi_period)
            fig.add_trace(go.Scatter(x=df['Date'], y=rsi, mode='lines', name=f'RSI({rsi_period})', line=dict(color='#607D8B', width=1.2)), row=row_rsi, col=1)
            # 30/70 lines
            x0, x1 = df['Date'].min(), df['Date'].max()
            yref = 'y' if row_rsi == 1 else f'y{row_rsi}'
            xref = 'x' if row_rsi == 1 else f'x{row_rsi}'
            fig.add_shape(type='line', x0=x0, x1=x1, xref=xref, y0=30, y1=30, yref=yref, line=dict(color='rgba(0,0,0,0.25)', width=1, dash='dot'))
            fig.add_shape(type='line', x0=x0, x1=x1, xref=xref, y0=70, y1=70, yref=yref, line=dict(color='rgba(0,0,0,0.25)', width=1, dash='dot'))
            fig.update_yaxes(range=[0, 100], row=row_rsi, col=1)

        # MACD panel
        if include_macd and row_macd is not None:
            macd, macd_signal, hist = self._compute_macd(df['Close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
            fig.add_trace(go.Bar(x=df['Date'], y=hist, name='MACD Hist', marker_color=['#26A69A' if v >= 0 else '#EF5350' for v in hist.fillna(0)]), row=row_macd, col=1)
            fig.add_trace(go.Scatter(x=df['Date'], y=macd, mode='lines', name='MACD', line=dict(color='#FF7043', width=1.2)), row=row_macd, col=1)
            fig.add_trace(go.Scatter(x=df['Date'], y=macd_signal, mode='lines', name='Signal', line=dict(color='#42A5F5', width=1)), row=row_macd, col=1)

        # Volume panel
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['Volume'], mode='lines', name="出来高", line=dict(color='#42A5F5', width=2), fill='tonexty', fillcolor='rgba(66,165,245,0.1)'),
            row=row_volume, col=1
        )

        # Layout and axes
        fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=350 + 200 * (rows_total - 1), showlegend=True, template="plotly_white")
        fig.update_xaxes(title_text="日付", row=row_volume, col=1)
        fig.update_yaxes(title_text="価格 (円)", row=row_price, col=1)
        fig.update_yaxes(title_text="出来高", row=row_volume, col=1)

        marks = self._parse_annotation_dates(df, annotate_dates, mark_month_start)
        self._add_date_annotations(fig, df, marks)
        self._apply_axis_ticks(fig, df, axis_tick=axis_tick, axis_tick_format=axis_tick_format, axis_tick_dates=axis_tick_dates, bottom_row=row_volume)

        return fig.to_dict()

    def create_candlestick_chart(self, df: pd.DataFrame, title: str = "ローソク足チャート", *, annotate_dates: Optional[List[str]] = None, mark_month_start: bool = False, axis_tick: str = "auto", axis_tick_format: Optional[str] = None, axis_tick_dates: Optional[List[str]] = None, **indicator_options) -> Dict[str, Any]:
        return self._build_chart(df, title, annotate_dates=annotate_dates, mark_month_start=mark_month_start, axis_tick=axis_tick, axis_tick_format=axis_tick_format, axis_tick_dates=axis_tick_dates, **indicator_options)
    
    def create_chart_with_indicators(self, df: pd.DataFrame, title: str = "ローソク足チャート", *, annotate_dates: Optional[List[str]] = None, mark_month_start: bool = False, axis_tick: str = "auto", axis_tick_format: Optional[str] = None, axis_tick_dates: Optional[List[str]] = None, **indicator_options) -> Dict[str, Any]:
        # with_indicators=True のデフォルト: MAと共に代表的指標を有効化
        defaults = dict(show_ma=True, show_bb=True, show_rsi=True, show_macd=True, show_vwap=True, show_mdd=True)
        merged = {**defaults, **(indicator_options or {})}
        return self._build_chart(df, title, annotate_dates=annotate_dates, mark_month_start=mark_month_start, axis_tick=axis_tick, axis_tick_format=axis_tick_format, axis_tick_dates=axis_tick_dates, **merged)
    
    def get_chart_data(self, filename: str, with_indicators: bool = False, *, annotate_dates: Optional[List[str]] = None, mark_month_start: bool = False, axis_tick: str = "auto", axis_tick_format: Optional[str] = None, axis_tick_dates: Optional[List[str]] = None, **indicator_options) -> Dict[str, Any]:
        try:
            df = self.load_csv_data(filename)
            ticker = filename.replace('.csv', '')
            title = f"{ticker} ローソク足チャート"
            if with_indicators:
                chart_data = self.create_chart_with_indicators(
                    df, title, annotate_dates=annotate_dates, mark_month_start=mark_month_start, axis_tick=axis_tick, axis_tick_format=axis_tick_format, axis_tick_dates=axis_tick_dates, **indicator_options
                )
            else:
                chart_data = self.create_candlestick_chart(
                    df, title, annotate_dates=annotate_dates, mark_month_start=mark_month_start, axis_tick=axis_tick, axis_tick_format=axis_tick_format, axis_tick_dates=axis_tick_dates, **indicator_options
                )
            return {
                "success": True,
                "data": chart_data,
                "ticker": ticker,
                "date_range": {
                    "start": df['Date'].min().strftime('%Y-%m-%d'),
                    "end": df['Date'].max().strftime('%Y-%m-%d')
                },
                "records_count": len(df)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
