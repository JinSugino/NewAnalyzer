from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder

from services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])
svc = AnalysisService()

@router.get("/summary")
async def get_summary(
    tickers: Optional[List[str]] = Query(None, description="分析対象のティッカー（ファイル名から .csv を除いたもの）"),
    risk_free_rate: float = Query(0.0, description="年率の無リスク金利 (例: 0.01=1%)"),
    periods_per_year: int = Query(252, description="年換算の期間数 (株式は252が一般的)"),
    method: str = Query("simple", description="リターン計算: simple または log")
):
    try:
        result = svc.get_summary(tickers, risk_free_rate=risk_free_rate, periods_per_year=periods_per_year, method=method)
        table_safe = json.loads(json.dumps(result["table"], default=str))
        return jsonable_encoder({"summary": result["summary"], "table": table_safe})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/html", response_class=HTMLResponse)
async def get_summary_html(
    tickers: Optional[List[str]] = Query(None),
    risk_free_rate: float = Query(0.0),
    periods_per_year: int = Query(252),
    method: str = Query("simple")
):
    result = svc.get_summary(tickers, risk_free_rate=risk_free_rate, periods_per_year=periods_per_year, method=method)
    fig_json = json.dumps(result["table"], default=str)
    html = f"""
    <!doctype html>
    <html lang=\"ja\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>統計量サマリ</title>
        <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
        <style>html, body {{ height: 100%; margin: 0; }} #chart {{ width: 100%; height: 100vh; }}</style>
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

@router.get("/correlation")
async def get_correlation(
    tickers: Optional[List[str]] = Query(None),
    method: str = Query("simple")
):
    try:
        result = svc.get_correlation(tickers, method=method)
        heatmap_safe = json.loads(json.dumps(result["heatmap"], default=str))
        return jsonable_encoder({"matrix": result["matrix"], "heatmap": heatmap_safe})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation/html", response_class=HTMLResponse)
async def get_correlation_html(
    tickers: Optional[List[str]] = Query(None),
    method: str = Query("simple")
):
    result = svc.get_correlation(tickers, method=method)
    fig_json = json.dumps(result["heatmap"], default=str)
    html = f"""
    <!doctype html>
    <html lang=\"ja\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>相関ヒートマップ</title>
        <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
        <style>html, body {{ height: 100%; margin: 0; }} #chart {{ width: 100%; height: 100vh; }}</style>
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

@router.get("/consolidated-correlation")
async def get_consolidated_correlation(
    tickers: Optional[List[str]] = Query(None, description="分析対象のティッカー（ファイル名から .csv を除いたもの）"),
    method: str = Query("simple", description="リターン計算: simple または log"),
    correlation_threshold: float = Query(0.9, description="相関統合の閾値 (0.9=90%)"),
    consolidation_method: str = Query("mean", description="統合方法: mean, median, first")
):
    try:
        result = svc.get_consolidated_correlation(
            tickers, 
            method=method,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method
        )
        original_heatmap_safe = json.loads(json.dumps(result["original_heatmap"], default=str))
        consolidated_heatmap_safe = json.loads(json.dumps(result["consolidated_heatmap"], default=str))
        return jsonable_encoder({
            "original_matrix": result["original_matrix"],
            "consolidated_matrix": result["consolidated_matrix"],
            "groups": result["groups"],
            "original_heatmap": original_heatmap_safe,
            "consolidated_heatmap": consolidated_heatmap_safe,
            "consolidation_info": result["consolidation_info"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/consolidated-correlation/html", response_class=HTMLResponse)
async def get_consolidated_correlation_html(
    tickers: Optional[List[str]] = Query(None),
    method: str = Query("simple"),
    correlation_threshold: float = Query(0.9),
    consolidation_method: str = Query("mean")
):
    result = svc.get_consolidated_correlation(
        tickers, 
        method=method,
        correlation_threshold=correlation_threshold,
        consolidation_method=consolidation_method
    )
    
    # 統合前後のヒートマップを並べて表示
    original_fig_json = json.dumps(result["original_heatmap"], default=str)
    consolidated_fig_json = json.dumps(result["consolidated_heatmap"], default=str)
    
    # グループ情報を表示用に整形
    groups_info = ""
    for i, group in enumerate(result["groups"], 1):
        if len(group) <= 3:
            groups_info += f"<p><strong>グループ{i}:</strong> {' + '.join(group)}</p>"
        else:
            groups_info += f"<p><strong>グループ{i}:</strong> {group[0]} + {len(group)-1}個の資産</p>"
    
    html = f"""
    <!doctype html>
    <html lang="ja">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>統合相関分析</title>
        <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
        <style>
          html, body {{ height: 100%; margin: 0; }}
          .container {{ display: flex; height: 100vh; }}
          .chart {{ flex: 1; }}
          .info {{ width: 300px; padding: 20px; background: #f5f5f5; overflow-y: auto; }}
          .info h3 {{ margin-top: 0; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="chart">
            <div id="original-chart" style="height: 50%;"></div>
            <div id="consolidated-chart" style="height: 50%;"></div>
          </div>
          <div class="info">
            <h3>統合情報</h3>
            <p><strong>閾値:</strong> {correlation_threshold}</p>
            <p><strong>統合方法:</strong> {consolidation_method}</p>
            <p><strong>元の資産数:</strong> {result["consolidation_info"]["original_assets"]}</p>
            <p><strong>統合後資産数:</strong> {result["consolidation_info"]["consolidated_assets"]}</p>
            <h3>相関グループ</h3>
            {groups_info}
          </div>
        </div>
        <script>
          const originalFig = {original_fig_json};
          const consolidatedFig = {consolidated_fig_json};
          Plotly.newPlot('original-chart', originalFig.data, originalFig.layout, {{responsive: true, displaylogo: false}});
          Plotly.newPlot('consolidated-chart', consolidatedFig.data, consolidatedFig.layout, {{responsive: true, displaylogo: false}});
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
