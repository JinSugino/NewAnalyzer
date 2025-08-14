from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder

from services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
svc = PortfolioService()

@router.get("/inputs")
async def get_inputs(
    tickers: Optional[List[str]] = Query(None, description="対象ティッカー（.csv除く）。未指定は全ファイル"),
    method: str = Query("simple", description="リターン計算: simple/log"),
    annualize: bool = Query(True, description="年率換算の有無"),
    periods_per_year: int = Query(252, description="年換算の期間数"),
    consolidate_correlated: bool = Query(False, description="相関統合の有無"),
    correlation_threshold: float = Query(0.9, description="相関統合の閾値"),
    consolidation_method: str = Query("mean", description="統合方法: mean/median/first")
):
    try:
        filenames = None
        if tickers:
            filenames = [f"{t}.csv" for t in tickers]
        result = svc.get_portfolio_inputs(
            filenames, 
            method=method, 
            annualize=annualize, 
            periods_per_year=periods_per_year,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method
        )
        return jsonable_encoder(json.loads(json.dumps(result, default=str)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feasible")
async def get_feasible(
    tickers: Optional[List[str]] = Query(None),
    method: str = Query("simple"),
    annualize: bool = Query(True),
    periods_per_year: int = Query(252),
    r_f: float = Query(0.0, description="無リスク利率(年率)"),
    allow_short: bool = Query(True, description="ショート許容"),
    target_return_min: Optional[float] = Query(None),
    target_return_max: Optional[float] = Query(None),
    num_frontier_points: int = Query(50),
    num_samples: int = Query(2000),
    max_leverage: float = Query(2.0),
    consolidate_correlated: bool = Query(False, description="相関統合の有無"),
    correlation_threshold: float = Query(0.9, description="相関統合の閾値"),
    consolidation_method: str = Query("mean", description="統合方法: mean/median/first")
):
    try:
        filenames = None
        if tickers:
            filenames = [f"{t}.csv" for t in tickers]
        result = svc.get_feasible_set_figure(
            filenames,
            method=method,
            annualize=annualize,
            periods_per_year=periods_per_year,
            r_f=r_f,
            allow_short=allow_short,
            target_return_min=target_return_min,
            target_return_max=target_return_max,
            num_frontier_points=num_frontier_points,
            num_samples=num_samples,
            max_leverage=max_leverage,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method,
        )
        return jsonable_encoder(json.loads(json.dumps(result, default=str)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feasible/html", response_class=HTMLResponse)
async def get_feasible_html(
    tickers: Optional[List[str]] = Query(None),
    method: str = Query("simple"),
    annualize: bool = Query(True),
    periods_per_year: int = Query(252),
    r_f: float = Query(0.0),
    allow_short: bool = Query(True),
    target_return_min: Optional[float] = Query(None),
    target_return_max: Optional[float] = Query(None),
    num_frontier_points: int = Query(50),
    num_samples: int = Query(2000),
    max_leverage: float = Query(2.0),
    consolidate_correlated: bool = Query(False),
    correlation_threshold: float = Query(0.9),
    consolidation_method: str = Query("mean")
):
    result = await get_feasible(
        tickers=tickers,
        method=method,
        annualize=annualize,
        periods_per_year=periods_per_year,
        r_f=r_f,
        allow_short=allow_short,
        target_return_min=target_return_min,
        target_return_max=target_return_max,
        num_frontier_points=num_frontier_points,
        num_samples=num_samples,
        max_leverage=max_leverage,
        consolidate_correlated=consolidate_correlated,
        correlation_threshold=correlation_threshold,
        consolidation_method=consolidation_method,
    )
    fig = result["figure"]
    fig_json = json.dumps(fig, default=str)
    html = f"""
    <!doctype html>
    <html lang=\"ja\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Feasible Set</title>
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

@router.get("/optimization/html", response_class=HTMLResponse)
async def get_optimization_html(
    tickers: Optional[List[str]] = Query(None),
    method: str = Query("simple"),
    annualize: bool = Query(True),
    periods_per_year: int = Query(252),
    r_f: float = Query(0.0),
    allow_short: bool = Query(True),
    num_frontier_points: int = Query(50),
    num_samples: int = Query(2000),
    max_leverage: float = Query(2.0),
    consolidate_correlated: bool = Query(False),
    correlation_threshold: float = Query(0.9),
    consolidation_method: str = Query("mean"),
    optimization_method: str = Query("sharpe", description="最適化方法: sharpe/min_variance/max_return"),
    target_return: Optional[float] = Query(None),
    target_risk: Optional[float] = Query(None),
    risk_tolerance: float = Query(1.0),
    max_weight: float = Query(1.0),
    min_weight: float = Query(0.0)
):
    try:
        filenames = None
        if tickers:
            filenames = [f"{t}.csv" for t in tickers]
        
        result = svc.get_optimization_figure(
            filenames,
            method=method,
            annualize=annualize,
            periods_per_year=periods_per_year,
            r_f=r_f,
            allow_short=allow_short,
            num_frontier_points=num_frontier_points,
            num_samples=num_samples,
            max_leverage=max_leverage,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method,
            optimization_method=optimization_method,
            target_return=target_return,
            target_risk=target_risk,
            risk_tolerance=risk_tolerance,
            max_weight=max_weight,
            min_weight=min_weight,
        )
        
        fig = result["figure"]
        fig_json = json.dumps(fig, default=str)
        html = f"""
        <!doctype html>
        <html lang="ja">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Portfolio Optimization</title>
            <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
            <style>html, body {{ height: 100%; margin: 0; }} #chart {{ width: 100%; height: 100vh; }}</style>
          </head>
          <body>
            <div id="chart"></div>
            <script>
              const fig = {fig_json};
              Plotly.newPlot('chart', fig.data, fig.layout, {{responsive: true, displaylogo: false}});
            </script>
          </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/efficient-frontier/html", response_class=HTMLResponse)
async def get_efficient_frontier_html(
    tickers: Optional[List[str]] = Query(None),
    method: str = Query("simple"),
    annualize: bool = Query(True),
    periods_per_year: int = Query(252),
    r_f: float = Query(0.0),
    allow_short: bool = Query(True),
    num_frontier_points: int = Query(50),
    num_samples: int = Query(2000),
    max_leverage: float = Query(2.0),
    consolidate_correlated: bool = Query(False),
    correlation_threshold: float = Query(0.9),
    consolidation_method: str = Query("mean"),
    optimization_method: str = Query("sharpe"),
    target_return: Optional[float] = Query(None),
    target_risk: Optional[float] = Query(None),
    risk_tolerance: float = Query(1.0),
    max_weight: float = Query(1.0),
    min_weight: float = Query(0.0)
):
    try:
        filenames = None
        if tickers:
            filenames = [f"{t}.csv" for t in tickers]
        
        result = svc.get_efficient_frontier_figure(
            filenames,
            method=method,
            annualize=annualize,
            periods_per_year=periods_per_year,
            r_f=r_f,
            allow_short=allow_short,
            num_frontier_points=num_frontier_points,
            num_samples=num_samples,
            max_leverage=max_leverage,
            consolidate_correlated=consolidate_correlated,
            correlation_threshold=correlation_threshold,
            consolidation_method=consolidation_method,
            optimization_method=optimization_method,
            target_return=target_return,
            target_risk=target_risk,
            risk_tolerance=risk_tolerance,
            max_weight=max_weight,
            min_weight=min_weight,
        )
        
        fig = result["figure"]
        fig_json = json.dumps(fig, default=str)
        html = f"""
        <!doctype html>
        <html lang="ja">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Efficient Frontier</title>
            <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
            <style>html, body {{ height: 100%; margin: 0; }} #chart {{ width: 100%; height: 100vh; }}</style>
          </head>
          <body>
            <div id="chart"></div>
            <script>
              const fig = {fig_json};
              Plotly.newPlot('chart', fig.data, fig.layout, {{responsive: true, displaylogo: false}});
            </script>
          </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
