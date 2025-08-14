import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import pandas as pd

from .base_provider import BaseDataProvider

# 外部依存をインポート（プロバイダー内でのみ使用）
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logging.warning("yfinance not available. Yahoo Finance provider will not work.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests not available. Some Yahoo Finance features may not work.")


class YahooFinanceProvider(BaseDataProvider):
    """Yahoo Financeからのデータ取得プロバイダー
    
    外部ライブラリ（yfinance, requests）の依存を完全に隠蔽し、
    標準化されたインターフェースを提供します。
    """
    
    def __init__(self):
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance is required for YahooFinanceProvider")
        
        self._provider_name = "Yahoo Finance"
        self._provider_version = "1.0.0"
        self._supported_exchanges = [
            "NYSE", "NASDAQ", "TOKYO", "LSE", "TSE", "ASX", "TSX"
        ]
        
        # レート制限情報
        self._rate_limits = {
            "requests_per_minute": 60,
            "requests_per_hour": 2000,
            "concurrent_requests": 5
        }
    
    def get_stock_data(
        self, 
        symbol: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Yahoo Financeから株価データを取得
        
        Args:
            symbol: 株式シンボル（例: "AAPL", "6758.T"）
            start_date: 開始日（Noneの場合は1年前）
            end_date: 終了日（Noneの場合は現在日）
            **kwargs: 追加パラメータ（interval, prepost等）
            
        Returns:
            標準化されたデータ辞書
        """
        try:
            # デフォルト日付の設定
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=365)
            
            # yfinanceを使用してデータ取得
            ticker = yf.Ticker(symbol)
            
            # データ取得パラメータ
            interval = kwargs.get("interval", "1d")
            prepost = kwargs.get("prepost", False)
            
            # データ取得
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                prepost=prepost
            )
            
            if df.empty:
                return {
                    "success": False,
                    "data": None,
                    "error": f"No data found for symbol: {symbol}",
                    "metadata": {
                        "symbol": symbol,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "provider": self._provider_name
                    }
                }
            
            # データを標準形式に変換
            data_list = []
            for index, row in df.iterrows():
                data_list.append({
                    "Date": index.strftime("%Y/%m/%d"),
                    "Open": float(row["Open"]),
                    "High": float(row["High"]),
                    "Low": float(row["Low"]),
                    "Close": float(row["Close"]),
                    "Volume": int(row["Volume"])
                })
            
            # メタデータの取得
            info = ticker.info
            metadata = {
                "symbol": symbol,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "provider": self._provider_name,
                "data_points": len(data_list),
                "company_name": info.get("longName", "Unknown"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "currency": info.get("currency", "Unknown"),
                "exchange": info.get("exchange", "Unknown")
            }
            
            return {
                "success": True,
                "data": data_list,
                "error": None,
                "metadata": metadata
            }
            
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {str(e)}")
            return {
                "success": False,
                "data": None,
                "error": f"Failed to fetch data: {str(e)}",
                "metadata": {
                    "symbol": symbol,
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "provider": self._provider_name
                }
            }
    
    def validate_symbol(self, symbol: str) -> bool:
        """シンボルの妥当性を検証
        
        Args:
            symbol: 検証するシンボル
            
        Returns:
            妥当なシンボルの場合True
        """
        try:
            if not symbol or not isinstance(symbol, str):
                return False
            
            # 基本的な形式チェック
            if len(symbol) < 1 or len(symbol) > 20:
                return False
            
            # yfinanceで実際に検証
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 有効なシンボルかチェック
            return info.get("regularMarketPrice") is not None
            
        except Exception:
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """プロバイダー情報を取得
        
        Returns:
            プロバイダー情報辞書
        """
        return {
            "name": self._provider_name,
            "version": self._provider_version,
            "description": "Yahoo Finance data provider using yfinance library",
            "supported_symbols": [
                "US stocks (e.g., AAPL, MSFT, GOOGL)",
                "Japanese stocks (e.g., 6758.T, 7203.T)",
                "International stocks (e.g., TSLA, AMZN)",
                "ETFs, indices, and other securities"
            ],
            "rate_limits": self._rate_limits,
            "data_available": [
                "OHLCV data",
                "Company information",
                "Historical data",
                "Real-time quotes (limited)"
            ]
        }
    
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """シンボルを検索
        
        Args:
            query: 検索クエリ
            
        Returns:
            検索結果のリスト
        """
        try:
            if not REQUESTS_AVAILABLE:
                return []
            
            # Yahoo Financeの検索APIを使用
            search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for quote in data.get("quotes", []):
                results.append({
                    "symbol": quote.get("symbol", ""),
                    "name": quote.get("longname", quote.get("shortname", "")),
                    "exchange": quote.get("exchange", ""),
                    "type": quote.get("quoteType", ""),
                    "market": quote.get("market", "")
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching symbols for '{query}': {str(e)}")
            return []
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """会社情報を取得（追加メソッド）
        
        Args:
            symbol: 株式シンボル
            
        Returns:
            会社情報辞書
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "name": info.get("longName", "Unknown"),
                    "short_name": info.get("shortName", "Unknown"),
                    "sector": info.get("sector", "Unknown"),
                    "industry": info.get("industry", "Unknown"),
                    "country": info.get("country", "Unknown"),
                    "currency": info.get("currency", "Unknown"),
                    "exchange": info.get("exchange", "Unknown"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "beta": info.get("beta"),
                    "website": info.get("website"),
                    "description": info.get("longBusinessSummary", "")
                },
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"Failed to fetch company info: {str(e)}"
            }
