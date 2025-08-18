from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chart_api import router as chart_router
from api.analysis_api import router as analysis_router
from api.portfolio_api import router as portfolio_router
from api.download_api import router as download_router
from api.currency_api import router as currency_router
import uvicorn

# FastAPIアプリケーションを作成
app = FastAPI(
    title="NewAnalyzer API",
    description="ローソク足チャート分析API",
    version="1.0.0"
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを登録
app.include_router(chart_router)
app.include_router(analysis_router)
app.include_router(portfolio_router)
app.include_router(download_router)
app.include_router(currency_router)

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "NewAnalyzer API",
        "version": "1.0.0",
        "endpoints": {
            "chart": "/chart",
            "analysis": "/analysis",
            "portfolio": "/portfolio",
            "download": "/download",
            "currency": "/currency",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # 開発サーバーを起動
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
