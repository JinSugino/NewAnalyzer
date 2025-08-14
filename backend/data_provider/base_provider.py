from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, date


class BaseDataProvider(ABC):
    """データプロバイダーの抽象基底クラス
    
    外部APIからのデータ取得を抽象化し、プロバイダー固有の実装を隠蔽します。
    新しいデータソースを追加する際は、このクラスを継承して実装してください。
    """
    
    @abstractmethod
    def get_stock_data(
        self, 
        symbol: str, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """株価データを取得する
        
        Args:
            symbol: 株式シンボル（例: "AAPL", "6758.T"）
            start_date: 開始日（Noneの場合はデフォルト値）
            end_date: 終了日（Noneの場合は現在日）
            **kwargs: プロバイダー固有のパラメータ
            
        Returns:
            標準化されたデータ辞書:
            {
                "success": bool,
                "data": Optional[List[Dict]],  # 成功時のみ
                "error": Optional[str],        # 失敗時のみ
                "metadata": Dict               # メタデータ
            }
        """
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """シンボルの妥当性を検証する
        
        Args:
            symbol: 検証するシンボル
            
        Returns:
            妥当なシンボルの場合True
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """プロバイダー情報を取得する
        
        Returns:
            プロバイダー情報辞書:
            {
                "name": str,
                "version": str,
                "description": str,
                "supported_symbols": List[str],
                "rate_limits": Dict[str, Any]
            }
        """
        pass
    
    @abstractmethod
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """シンボルを検索する
        
        Args:
            query: 検索クエリ
            
        Returns:
            検索結果のリスト:
            [
                {
                    "symbol": str,
                    "name": str,
                    "exchange": str,
                    "type": str
                }
            ]
        """
        pass
