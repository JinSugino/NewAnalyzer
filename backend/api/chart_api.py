from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from services.chart_service import ChartService
import os
import json
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/chart", tags=["chart"])
chart_service = ChartService()

_indicator_desc = "with_indicators=true でデフォルト全有効。個別制御も可能。"

@router.get("/candlestick/{filename}")
async def get_candlestick_chart(
    filename: str,
    with_indicators: bool = Query(False, description="代表的指標を一括有効化"),
    # 注釈/軸
    annotate_dates: Optional[List[str]] = Query(None, description="注釈日付 YYYY-MM-DD/ YYYY/MM/DD"),
    mark_month_start: bool = Query(False, description="各月の最初の営業日に縦線注釈"),
    axis_tick: str = Query("auto", description="x軸ティック: auto/day/week/month/quarter/year/array"),
    axis_tick_format: Optional[str] = Query(None, description="tickラベルのフォーマット (例: %Y-%m-%d)"),
    axis_tick_dates: Optional[List[str]] = Query(None, description="axis_tick=array の場合の手動ティック日付群"),
    # 個別インジケータ
    show_ma: Optional[bool] = Query(None, description=_indicator_desc),
    ma_windows: Optional[List[int]] = Query(None, description="移動平均の窓長(複数可)"),
    show_bb: Optional[bool] = Query(None, description="ボリンジャーバンド"),
    bb_window: int = Query(20, description="BBの窓長"),
    bb_std: float = Query(2.0, description="BBの標準偏差倍率"),
    show_rsi: Optional[bool] = Query(None, description="RSIを表示"),
    rsi_period: int = Query(14, description="RSIの期間"),
    show_macd: Optional[bool] = Query(None, description="MACDを表示"),
    macd_fast: int = Query(12, description="MACD fast"),
    macd_slow: int = Query(26, description="MACD slow"),
    macd_signal: int = Query(9, description="MACD signal"),
    show_vwap: Optional[bool] = Query(None, description="VWAPを表示"),
    show_mdd: Optional[bool] = Query(None, description="最大ドローダウン区間をハイライト")
):
    try:
        if not filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="ファイルはCSV形式である必要があります")
        options = {
            "show_ma": show_ma, "ma_windows": ma_windows,
            "show_bb": show_bb, "bb_window": bb_window, "bb_std": bb_std,
            "show_rsi": show_rsi, "rsi_period": rsi_period,
            "show_macd": show_macd, "macd_fast": macd_fast, "macd_slow": macd_slow, "macd_signal": macd_signal,
            "show_vwap": show_vwap,
            "show_mdd": show_mdd,
        }
        # None は渡さない（デフォルトに任せる）
        options = {k: v for k, v in options.items() if v is not None}
        result = chart_service.get_chart_data(
            filename,
            with_indicators,
            annotate_dates=annotate_dates,
            mark_month_start=mark_month_start,
            axis_tick=axis_tick,
            axis_tick_format=axis_tick_format,
            axis_tick_dates=axis_tick_dates,
            **options
        )
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        safe_data = json.loads(json.dumps(result["data"], default=str))
        safe_result = {**{k: v for k, v in result.items() if k != "data"}, "data": safe_data}
        return jsonable_encoder(safe_result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバーエラー: {str(e)}")

@router.get("/html/{filename}", response_class=HTMLResponse)
async def get_candlestick_chart_html(
    filename: str,
    with_indicators: bool = Query(False, description="代表的指標を一括有効化"),
    annotate_dates: Optional[List[str]] = Query(None),
    mark_month_start: bool = Query(False),
    axis_tick: str = Query("auto"),
    axis_tick_format: Optional[str] = Query(None),
    axis_tick_dates: Optional[List[str]] = Query(None),
    show_ma: Optional[bool] = Query(None),
    ma_windows: Optional[List[int]] = Query(None),
    show_bb: Optional[bool] = Query(None),
    bb_window: int = Query(20),
    bb_std: float = Query(2.0),
    show_rsi: Optional[bool] = Query(None),
    rsi_period: int = Query(14),
    show_macd: Optional[bool] = Query(None),
    macd_fast: int = Query(12),
    macd_slow: int = Query(26),
    macd_signal: int = Query(9),
    show_vwap: Optional[bool] = Query(None),
    show_mdd: Optional[bool] = Query(None),
):
    try:
        if not filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="ファイルはCSV形式である必要があります")
        options = {
            "show_ma": show_ma, "ma_windows": ma_windows,
            "show_bb": show_bb, "bb_window": bb_window, "bb_std": bb_std,
            "show_rsi": show_rsi, "rsi_period": rsi_period,
            "show_macd": show_macd, "macd_fast": macd_fast, "macd_slow": macd_slow, "macd_signal": macd_signal,
            "show_vwap": show_vwap,
            "show_mdd": show_mdd,
        }
        options = {k: v for k, v in options.items() if v is not None}
        result = chart_service.get_chart_data(
            filename,
            with_indicators,
            annotate_dates=annotate_dates,
            mark_month_start=mark_month_start,
            axis_tick=axis_tick,
            axis_tick_format=axis_tick_format,
            axis_tick_dates=axis_tick_dates,
            **options
        )
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "不明なエラー"))
        fig_dict = result["data"]
        title = result.get("ticker", "Chart")
        fig_json = json.dumps(fig_dict, default=str)
        html = f"""
        <!doctype html>
        <html lang=\"ja\">
          <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
            <title>{title} チャート</title>
            <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
            <style>
              html, body {{ height: 100%; margin: 0; }}
              #chart {{ width: 100%; height: 100vh; }}
            </style>
          </head>
          <body>
            <div id=\"chart\"></div>
            <script>
              const fig = {fig_json};
              Plotly.newPlot('chart', fig.data, fig.layout, {{responsive: true, displaylogo: false}});
            </script>
          </body>
        </html>
        """
        return HTMLResponse(content=html)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバーエラー: {str(e)}")

@router.get("/json/{filename}")
async def get_candlestick_chart_json(
    filename: str,
    with_indicators: bool = Query(False, description="代表的指標を一括有効化"),
    annotate_dates: Optional[List[str]] = Query(None),
    mark_month_start: bool = Query(False),
    axis_tick: str = Query("auto"),
    axis_tick_format: Optional[str] = Query(None),
    axis_tick_dates: Optional[List[str]] = Query(None),
    show_ma: Optional[bool] = Query(None),
    ma_windows: Optional[List[int]] = Query(None),
    show_bb: Optional[bool] = Query(None),
    bb_window: int = Query(20),
    bb_std: float = Query(2.0),
    show_rsi: Optional[bool] = Query(None),
    rsi_period: int = Query(14),
    show_macd: Optional[bool] = Query(None),
    macd_fast: int = Query(12),
    macd_slow: int = Query(26),
    macd_signal: int = Query(9),
    show_vwap: Optional[bool] = Query(None),
    show_mdd: Optional[bool] = Query(None),
):
    try:
        if not filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="ファイルはCSV形式である必要があります")
        options = {
            "show_ma": show_ma, "ma_windows": ma_windows,
            "show_bb": show_bb, "bb_window": bb_window, "bb_std": bb_std,
            "show_rsi": show_rsi, "rsi_period": rsi_period,
            "show_macd": show_macd, "macd_fast": macd_fast, "macd_slow": macd_slow, "macd_signal": macd_signal,
            "show_vwap": show_vwap,
            "show_mdd": show_mdd,
        }
        options = {k: v for k, v in options.items() if v is not None}
        result = chart_service.get_chart_data(
            filename,
            with_indicators,
            annotate_dates=annotate_dates,
            mark_month_start=mark_month_start,
            axis_tick=axis_tick,
            axis_tick_format=axis_tick_format,
            axis_tick_dates=axis_tick_dates,
            **options
        )
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "不明なエラー"))
        
        # JSONデータを直接返す
        return {
            "success": True,
            "data": result["data"],
            "ticker": result.get("ticker", "Chart"),
            "html_content": f"""
            <!doctype html>
            <html lang="ja">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>{result.get("ticker", "Chart")} チャート</title>
                <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
                <style>
                  html, body {{ height: 100%; margin: 0; }}
                  #chart {{ width: 100%; height: 100vh; }}
                </style>
              </head>
              <body>
                <div id="chart"></div>
                <script>
                  const fig = {json.dumps(result["data"], default=str)};
                  Plotly.newPlot('chart', fig.data, fig.layout, {{responsive: true, displaylogo: false}});
                </script>
              </body>
            </html>
            """
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバーエラー: {str(e)}")

@router.get("/available-files")
async def get_available_files():
    try:
        data_dir = chart_service.data_dir
        if not os.path.exists(data_dir):
            return {"files": [], "message": "データディレクトリが存在しません"}
        csv_files = []
        for file in os.listdir(data_dir):
            if file.endswith('.csv'):
                csv_files.append(file)
        return {"files": csv_files, "count": len(csv_files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバーエラー: {str(e)}")

@router.get("/file-info/{filename}")
async def get_file_info(filename: str):
    try:
        if not filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="ファイルはCSV形式である必要があります")
        df = chart_service.load_csv_data(filename)
        price_stats = {
            "open": {
                "min": float(df['Open'].min()),
                "max": float(df['Open'].max()),
                "mean": float(df['Open'].mean()),
                "std": float(df['Open'].std())
            },
            "high": {
                "min": float(df['High'].min()),
                "max": float(df['High'].max()),
                "mean": float(df['High'].mean()),
                "std": float(df['High'].std())
            },
            "low": {
                "min": float(df['Low'].min()),
                "max": float(df['Low'].max()),
                "mean": float(df['Low'].mean()),
                "std": float(df['Low'].std())
            },
            "close": {
                "min": float(df['Close'].min()),
                "max": float(df['Close'].max()),
                "mean": float(df['Close'].mean()),
                "std": float(df['Close'].std())
            },
            "volume": {
                "min": float(df['Volume'].min()),
                "max": float(df['Volume'].max()),
                "mean": float(df['Volume'].mean()),
                "std": float(df['Volume'].std())
            }
        }
        return {
            "filename": filename,
            "ticker": filename.replace('.csv', ''),
            "date_range": {
                "start": df['Date'].min().strftime('%Y-%m-%d'),
                "end": df['Date'].max().strftime('%Y-%m-%d')
            },
            "records_count": len(df),
            "statistics": price_stats
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバーエラー: {str(e)}")
