from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
import json
from datetime import date
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from services.download_service import DownloadService
from data_provider.yahoo_provider import YahooFinanceProvider

router = APIRouter(prefix="/download", tags=["download"])

# サービスの初期化とプロバイダーの登録
svc = DownloadService()
try:
    yahoo_provider = YahooFinanceProvider()
    svc.register_provider("yahoo", yahoo_provider)
except ImportError as e:
    print(f"Warning: Yahoo Finance provider not available: {e}")

# Pydanticモデル
class DownloadRequest(BaseModel):
    symbol: str
    provider: str = "yahoo"
    interval: str = "1d"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    prepost: bool = False

@router.post("/")
async def download_data(request: DownloadRequest):
    """株価データをダウンロード（POST）"""
    try:
        # 日付の変換
        start_dt = None
        end_dt = None
        
        if request.start_date:
            try:
                start_dt = date.fromisoformat(request.start_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if request.end_date:
            try:
                end_dt = date.fromisoformat(request.end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # ダウンロード実行
        result = svc.download_stock_data(
            symbol=request.symbol,
            provider_name=request.provider,
            start_date=start_dt,
            end_date=end_dt,
            filename=None,
            interval=request.interval,
            prepost=request.prepost
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "symbol": request.symbol,
            "provider": request.provider,
            "file_path": result["file_path"],
            "data_points": result["data_points"],
            "metadata": result["metadata"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_providers():
    """利用可能なデータプロバイダー一覧を取得"""
    try:
        providers = svc.get_available_providers()
        provider_info = {}
        
        for provider_name in providers:
            info = svc.get_provider_info(provider_name)
            if info:
                provider_info[provider_name] = info
        
        return {
            "available_providers": providers,
            "provider_info": provider_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/provider/{provider_name}/info")
async def get_provider_info(provider_name: str):
    """指定したプロバイダーの詳細情報を取得"""
    try:
        info = svc.get_provider_info(provider_name)
        if info is None:
            raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")
        
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_symbols(
    query: str = Query(..., description="検索クエリ"),
    provider_name: str = Query("yahoo", description="使用するプロバイダー名")
):
    """シンボルを検索"""
    try:
        results = svc.search_symbols(query, provider_name)
        return {
            "query": query,
            "provider": provider_name,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{symbol}")
async def get_company_info(
    symbol: str,
    provider_name: str = Query("yahoo", description="使用するプロバイダー名")
):
    """会社情報を取得"""
    try:
        info = svc.get_company_info(symbol, provider_name)
        if info is None:
            raise HTTPException(status_code=404, detail=f"Company info not found for {symbol}")
        
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-download")
async def batch_download(
    symbols: List[str] = Query(..., description="ダウンロードするシンボルのリスト"),
    provider_name: str = Query("yahoo", description="使用するプロバイダー名"),
    start_date: Optional[str] = Query(None, description="開始日（YYYY-MM-DD形式）"),
    end_date: Optional[str] = Query(None, description="終了日（YYYY-MM-DD形式）"),
    interval: str = Query("1d", description="データ間隔"),
    prepost: bool = Query(False, description="前後場データを含むか")
):
    """複数シンボルの一括ダウンロード"""
    try:
        # 日付の変換
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = date.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = date.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # 一括ダウンロード実行
        result = svc.batch_download(
            symbols=symbols,
            provider_name=provider_name,
            start_date=start_dt,
            end_date=end_dt,
            interval=interval,
            prepost=prepost
        )
        
        return {
            "total": result["total"],
            "success_count": result["success_count"],
            "failed_count": result["failed_count"],
            "success": result["success"],
            "failed": result["failed"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files():
    """ダウンロード済みファイル一覧を取得"""
    try:
        files = svc.list_downloaded_files()
        return {
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """ファイルを削除"""
    try:
        success = svc.delete_file(filename)
        if not success:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
        
        return {
            "success": True,
            "message": f"File '{filename}' deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/symbol/{symbol}")
async def delete_files_by_symbol(symbol: str):
    """シンボルに関連するファイルを削除"""
    try:
        result = svc.delete_files_by_symbol(symbol)
        if not result["success"] and "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/batch")
async def delete_multiple_files(
    filenames: List[str] = Query(..., description="削除するファイル名のリスト")
):
    """複数ファイルを一括削除"""
    try:
        if not filenames:
            raise HTTPException(status_code=400, detail="No filenames provided")
        
        result = svc.delete_multiple_files(filenames)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/all")
async def delete_all_files():
    """全てのダウンロード済みファイルを削除"""
    try:
        result = svc.delete_all_files()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{filename}/info")
async def get_file_info(filename: str):
    """ファイル情報を取得"""
    try:
        info = svc.get_file_info(filename)
        if info is None:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
        
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/info")
async def get_all_files_info():
    """全てのファイルの情報を取得"""
    try:
        files = svc.list_downloaded_files()
        files_info = []
        
        for filename in files:
            info = svc.get_file_info(filename)
            if info:
                files_info.append(info)
        
        return {
            "files": files_info,
            "count": len(files_info),
            "total_size_bytes": sum(f["size_bytes"] for f in files_info),
            "total_size_readable": _format_size(sum(f["size_bytes"] for f in files_info))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _format_size(size_bytes: int) -> str:
    """ファイルサイズを読みやすい形式に変換"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

@router.get("/validate/{symbol}")
async def validate_symbol(
    symbol: str,
    provider_name: str = Query("yahoo", description="使用するプロバイダー名")
):
    """シンボルの妥当性を検証"""
    try:
        if provider_name not in svc.get_available_providers():
            raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")
        
        provider = svc._providers[provider_name]
        is_valid = provider.validate_symbol(symbol)
        
        return {
            "symbol": symbol,
            "provider": provider_name,
            "is_valid": is_valid
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
