from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.currency_service import CurrencyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/currency", tags=["currency"])

class CurrencyConversionRequest(BaseModel):
    files: List[str]
    target_currency: str = "USD"  # "USD" or "JPY"

class CurrencyConversionResponse(BaseModel):
    success: bool
    converted_files: Dict[str, str]
    message: str

@router.post("/download-exchange-rate")
async def download_exchange_rate():
    """
    為替レートデータをダウンロード
    """
    try:
        currency_service = CurrencyService()
        success = currency_service.download_exchange_rate()
        
        if success:
            return {"success": True, "message": "Exchange rate data downloaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to download exchange rate data")
            
    except Exception as e:
        logger.error(f"Error in download_exchange_rate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert", response_model=CurrencyConversionResponse)
async def convert_currency(request: CurrencyConversionRequest):
    """
    指定されたファイルを指定された通貨に換算
    """
    try:
        currency_service = CurrencyService()
        
        # 為替レートデータが存在するかチェック
        exchange_rates = currency_service.get_exchange_rate_data()
        if exchange_rates.empty:
            # 為替レートデータが存在しない場合はダウンロード
            success = currency_service.download_exchange_rate()
            if not success:
                raise HTTPException(status_code=500, detail="Failed to download exchange rate data")
        
        # 通貨換算を実行
        converted_files = currency_service.generate_analysis_data(
            request.files, 
            request.target_currency
        )
        
        return CurrencyConversionResponse(
            success=True,
            converted_files=converted_files,
            message=f"Successfully converted {len(converted_files)} files to {request.target_currency}"
        )
        
    except Exception as e:
        logger.error(f"Error in convert_currency: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exchange-rate-status")
async def get_exchange_rate_status():
    """
    為替レートデータの状態を確認
    """
    try:
        currency_service = CurrencyService()
        exchange_rates = currency_service.get_exchange_rate_data()
        
        if not exchange_rates.empty:
            return {
                "available": True,
                "data_points": len(exchange_rates),
                "date_range": {
                    "start": exchange_rates['Date'].min().isoformat(),
                    "end": exchange_rates['Date'].max().isoformat()
                }
            }
        else:
            return {
                "available": False,
                "message": "Exchange rate data not available"
            }
            
    except Exception as e:
        logger.error(f"Error in get_exchange_rate_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
