import os
import logging
from typing import Dict, List, Optional, Any
from datetime import date, datetime
import pandas as pd

from data_provider.base_provider import BaseDataProvider


class DownloadService:
    """データダウンロードサービス
    
    プロバイダーに依存しない疎結合設計で、データプロバイダーから
    データを取得し、CSVファイルとして保存する機能を提供します。
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._providers: Dict[str, BaseDataProvider] = {}
        
        # データディレクトリの作成
        os.makedirs(self.data_dir, exist_ok=True)
        
        logging.info(f"DownloadService initialized with data directory: {self.data_dir}")
    
    def register_provider(self, name: str, provider: BaseDataProvider) -> None:
        """データプロバイダーを登録
        
        Args:
            name: プロバイダー名
            provider: データプロバイダーインスタンス
        """
        self._providers[name] = provider
        logging.info(f"Registered provider: {name}")
    
    def get_available_providers(self) -> List[str]:
        """利用可能なプロバイダー一覧を取得
        
        Returns:
            プロバイダー名のリスト
        """
        return list(self._providers.keys())
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """プロバイダー情報を取得
        
        Args:
            provider_name: プロバイダー名
            
        Returns:
            プロバイダー情報辞書（存在しない場合はNone）
        """
        if provider_name not in self._providers:
            return None
        
        return self._providers[provider_name].get_provider_info()
    
    def download_stock_data(
        self,
        symbol: str,
        provider_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        filename: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """株価データをダウンロードしてCSVファイルに保存
        
        Args:
            symbol: 株式シンボル
            provider_name: 使用するプロバイダー名
            start_date: 開始日
            end_date: 終了日
            filename: 保存するファイル名（Noneの場合は自動生成）
            **kwargs: プロバイダー固有のパラメータ
            
        Returns:
            ダウンロード結果辞書
        """
        try:
            # プロバイダーの存在確認
            if provider_name not in self._providers:
                return {
                    "success": False,
                    "error": f"Provider '{provider_name}' not found. Available: {self.get_available_providers()}",
                    "file_path": None
                }
            
            provider = self._providers[provider_name]
            
            # シンボルの妥当性検証
            if not provider.validate_symbol(symbol):
                return {
                    "success": False,
                    "error": f"Invalid symbol: {symbol}",
                    "file_path": None
                }
            
            # データ取得
            result = provider.get_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                **kwargs
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "file_path": None
                }
            
            # ファイル名の生成
            if filename is None:
                filename = f"{symbol}.csv"
            
            # ファイルパスの生成
            file_path = os.path.join(self.data_dir, filename)
            
            # CSVファイルとして保存
            self._save_to_csv(result["data"], file_path, symbol)
            
            return {
                "success": True,
                "error": None,
                "file_path": file_path,
                "metadata": result["metadata"],
                "data_points": len(result["data"])
            }
            
        except Exception as e:
            logging.error(f"Error downloading data for {symbol}: {str(e)}")
            return {
                "success": False,
                "error": f"Download failed: {str(e)}",
                "file_path": None
            }
    
    def search_symbols(self, query: str, provider_name: str) -> List[Dict[str, Any]]:
        """シンボルを検索
        
        Args:
            query: 検索クエリ
            provider_name: 使用するプロバイダー名
            
        Returns:
            検索結果のリスト
        """
        try:
            if provider_name not in self._providers:
                return []
            
            provider = self._providers[provider_name]
            return provider.search_symbols(query)
            
        except Exception as e:
            logging.error(f"Error searching symbols: {str(e)}")
            return []
    
    def get_company_info(self, symbol: str, provider_name: str) -> Optional[Dict[str, Any]]:
        """会社情報を取得
        
        Args:
            symbol: 株式シンボル
            provider_name: 使用するプロバイダー名
            
        Returns:
            会社情報辞書（取得できない場合はNone）
        """
        try:
            if provider_name not in self._providers:
                return None
            
            provider = self._providers[provider_name]
            
            # プロバイダーに会社情報取得メソッドがある場合
            if hasattr(provider, 'get_company_info'):
                result = provider.get_company_info(symbol)
                return result if result["success"] else None
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting company info: {str(e)}")
            return None
    
    def batch_download(
        self,
        symbols: List[str],
        provider_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """複数シンボルの一括ダウンロード
        
        Args:
            symbols: シンボルのリスト
            provider_name: 使用するプロバイダー名
            start_date: 開始日
            end_date: 終了日
            **kwargs: プロバイダー固有のパラメータ
            
        Returns:
            一括ダウンロード結果辞書
        """
        results = {
            "success": [],
            "failed": [],
            "total": len(symbols),
            "success_count": 0,
            "failed_count": 0
        }
        
        for symbol in symbols:
            result = self.download_stock_data(
                symbol=symbol,
                provider_name=provider_name,
                start_date=start_date,
                end_date=end_date,
                **kwargs
            )
            
            if result["success"]:
                results["success"].append({
                    "symbol": symbol,
                    "file_path": result["file_path"],
                    "data_points": result["data_points"]
                })
                results["success_count"] += 1
            else:
                results["failed"].append({
                    "symbol": symbol,
                    "error": result["error"]
                })
                results["failed_count"] += 1
        
        return results
    
    def _save_to_csv(self, data: List[Dict[str, Any]], file_path: str, symbol: str) -> None:
        """データをCSVファイルとして保存
        
        Args:
            data: 保存するデータ
            file_path: 保存先ファイルパス
            symbol: シンボル名
        """
        # データフレームの作成
        df = pd.DataFrame(data)
        
        # ヘッダー行の追加（既存のCSV形式に合わせる）
        header_rows = [
            ["Price", "Open", "High", "Low", "Close", "Volume"],
            ["Ticker", symbol, symbol, symbol, symbol, symbol],
            ["Date"]
        ]
        
        # CSVファイルとして保存
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            # ヘッダー行を書き込み
            for header_row in header_rows:
                f.write(','.join(header_row) + '\n')
            
            # データ行を書き込み
            for _, row in df.iterrows():
                f.write(f"{row['Date']}, {row['Open']}, {row['High']}, {row['Low']}, {row['Close']}, {row['Volume']}\n")
        
        logging.info(f"Data saved to: {file_path}")
    
    def list_downloaded_files(self) -> List[str]:
        """ダウンロード済みファイル一覧を取得
        
        Returns:
            ファイル名のリスト
        """
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            return sorted(files)
        except Exception as e:
            logging.error(f"Error listing files: {str(e)}")
            return []
    
    def delete_file(self, filename: str) -> bool:
        """ファイルを削除
        
        Args:
            filename: 削除するファイル名
            
        Returns:
            削除成功の場合True
        """
        try:
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"File deleted: {file_path}")
                return True
            else:
                logging.warning(f"File not found: {file_path}")
                return False
        except Exception as e:
            logging.error(f"Error deleting file {filename}: {str(e)}")
            return False
    
    def delete_files_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """シンボルに関連するファイルを削除
        
        Args:
            symbol: 削除するシンボル
            
        Returns:
            削除結果辞書
        """
        try:
            files = self.list_downloaded_files()
            matching_files = [f for f in files if f.startswith(f"{symbol}.") or f == f"{symbol}.csv"]
            
            if not matching_files:
                return {
                    "success": False,
                    "deleted_files": [],
                    "error": f"No files found for symbol: {symbol}"
                }
            
            deleted_files = []
            failed_files = []
            
            for filename in matching_files:
                if self.delete_file(filename):
                    deleted_files.append(filename)
                else:
                    failed_files.append(filename)
            
            return {
                "success": len(failed_files) == 0,
                "symbol": symbol,
                "deleted_files": deleted_files,
                "failed_files": failed_files,
                "total_found": len(matching_files),
                "total_deleted": len(deleted_files),
                "total_failed": len(failed_files)
            }
            
        except Exception as e:
            logging.error(f"Error deleting files for symbol {symbol}: {str(e)}")
            return {
                "success": False,
                "symbol": symbol,
                "deleted_files": [],
                "failed_files": [],
                "error": f"Failed to delete files: {str(e)}"
            }
    
    def delete_multiple_files(self, filenames: List[str]) -> Dict[str, Any]:
        """複数ファイルを一括削除
        
        Args:
            filenames: 削除するファイル名のリスト
            
        Returns:
            一括削除結果辞書
        """
        try:
            deleted_files = []
            failed_files = []
            
            for filename in filenames:
                if self.delete_file(filename):
                    deleted_files.append(filename)
                else:
                    failed_files.append(filename)
            
            return {
                "success": len(failed_files) == 0,
                "deleted_files": deleted_files,
                "failed_files": failed_files,
                "total_requested": len(filenames),
                "total_deleted": len(deleted_files),
                "total_failed": len(failed_files)
            }
            
        except Exception as e:
            logging.error(f"Error in batch delete: {str(e)}")
            return {
                "success": False,
                "deleted_files": [],
                "failed_files": [],
                "error": f"Batch delete failed: {str(e)}"
            }
    
    def delete_all_files(self) -> Dict[str, Any]:
        """全てのダウンロード済みファイルを削除
        
        Returns:
            削除結果辞書
        """
        try:
            files = self.list_downloaded_files()
            
            if not files:
                return {
                    "success": True,
                    "deleted_files": [],
                    "message": "No files to delete"
                }
            
            deleted_files = []
            failed_files = []
            
            for filename in files:
                if self.delete_file(filename):
                    deleted_files.append(filename)
                else:
                    failed_files.append(filename)
            
            return {
                "success": len(failed_files) == 0,
                "deleted_files": deleted_files,
                "failed_files": failed_files,
                "total_files": len(files),
                "total_deleted": len(deleted_files),
                "total_failed": len(failed_files)
            }
            
        except Exception as e:
            logging.error(f"Error deleting all files: {str(e)}")
            return {
                "success": False,
                "deleted_files": [],
                "failed_files": [],
                "error": f"Failed to delete all files: {str(e)}"
            }
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """ファイル情報を取得
        
        Args:
            filename: ファイル名
            
        Returns:
            ファイル情報辞書（存在しない場合はNone）
        """
        try:
            file_path = os.path.join(self.data_dir, filename)
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            # ファイルサイズを読みやすい形式に変換
            size_bytes = stat.st_size
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            return {
                "filename": filename,
                "file_path": file_path,
                "size_bytes": size_bytes,
                "size_readable": size_str,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }
            
        except Exception as e:
            logging.error(f"Error getting file info for {filename}: {str(e)}")
            return None
