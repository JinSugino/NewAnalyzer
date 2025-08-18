import pandas as pd
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CurrencyService:
    """
    通貨換算機能を提供するサービス
    - 為替レートの取得・管理
    - 株価データの通貨換算
    - 分析用データの生成・管理
    """
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.analysis_dir = os.path.join(os.path.dirname(__file__), '..', 'data_analysis')
        self.exchange_rate_file = os.path.join(self.data_dir, 'USDJPY.csv')
        self.metadata_file = os.path.join(self.analysis_dir, 'metadata.json')
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(self.analysis_dir, exist_ok=True)
    
    def _is_alphabetic_ticker(self, ticker: str) -> bool:
        """
        ティッカーが英字のみかどうかを判定
        例: "SPY" -> True, "7203" -> False, "7203.T" -> False
        """
        return ticker.isalpha()
    
    def get_exchange_rate_data(self) -> pd.DataFrame:
        """
        為替レートデータを取得
        """
        if os.path.exists(self.exchange_rate_file):
            df = pd.read_csv(self.exchange_rate_file)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        else:
            logger.warning("USDJPY.csv not found. Please download exchange rate data first.")
            return pd.DataFrame()
    
    def download_exchange_rate(self) -> bool:
        """
       為替レートデータをダウンロード
        """
        try:
            import yfinance as yf
            
            # 過去5年間の為替レートを取得
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5*365)
            
            usdjpy = yf.download('USDJPY=X', start=start_date, end=end_date)
            
            if not usdjpy.empty:
                # CSV形式で保存
                usdjpy.reset_index().to_csv(self.exchange_rate_file, index=False)
                logger.info(f"Exchange rate data downloaded and saved to {self.exchange_rate_file}")
                return True
            else:
                logger.error("Failed to download exchange rate data")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading exchange rate: {e}")
            return False
    
    def identify_currency(self, ticker: str) -> str:
        """
        ティッカーから通貨を識別
        """
        if ticker.endswith('.T'):
            return 'JPY'  # 日本株
        else:
            return 'USD'  # 米国株
    
    def convert_currency(self, df: pd.DataFrame, from_currency: str, to_currency: str, 
                        exchange_rates: pd.DataFrame) -> pd.DataFrame:
        """
        株価データを指定された通貨に換算
        """
        if from_currency == to_currency:
            return df.copy()
        
        result_df = df.copy()
        
        # 特殊なCSV構造に対応（最初の2行をスキップしてDateカラムを設定）
        if 'Date' not in result_df.columns and len(result_df.columns) >= 6:
            # 3行目以降のデータを使用し、最初の列をDateとして設定
            result_df = result_df.iloc[2:].reset_index(drop=True)
            result_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            
            # 空のDate行を削除
            result_df = result_df.dropna(subset=['Date'])
            result_df = result_df[result_df['Date'] != '']
            
            # 数値列を数値型に変換
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
        
        result_df['Date'] = pd.to_datetime(result_df['Date'])
        
        # 為替レートとマージ
        merged_df = pd.merge(result_df, exchange_rates[['Date', 'Close']], 
                           on='Date', how='left', suffixes=('', '_rate'))
        
        # 通貨換算
        if from_currency == 'USD' and to_currency == 'JPY':
            # ドルから円への換算
            price_columns = ['Open', 'High', 'Low', 'Close']
            for col in price_columns:
                if col in merged_df.columns:
                    merged_df[col] = merged_df[col] * merged_df['Close_rate']
            
            # Volumeは通貨換算しない（株数は変わらない）
            
        elif from_currency == 'JPY' and to_currency == 'USD':
            # 円からドルへの換算
            price_columns = ['Open', 'High', 'Low', 'Close']
            for col in price_columns:
                if col in merged_df.columns:
                    merged_df[col] = merged_df[col] / merged_df['Close_rate']
        
        # 為替レート列を削除
        merged_df = merged_df.drop('Close_rate', axis=1)
        
        return merged_df
    
    def generate_analysis_data(self, files: List[str], target_currency: str) -> Dict[str, str]:
        """
        分析用データを生成
        """
        exchange_rates = self.get_exchange_rate_data()
        if exchange_rates.empty:
            logger.warning("Exchange rate data not available. Attempting to download...")
            if not self.download_exchange_rate():
                logger.error("Failed to download exchange rate data")
                return {}
            exchange_rates = self.get_exchange_rate_data()
            if exchange_rates.empty:
                logger.error("Exchange rate data still not available after download attempt")
                return {}
        
        converted_files = {}
        
        for file in files:
            file_path = os.path.join(self.data_dir, file)
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            # ティッカーを抽出（ファイル名から.csvを除去）
            ticker = file.replace('.csv', '')
            
            # 英字ファイル名のみ変換。英字以外は変換せず元ファイルを使用
            if not self._is_alphabetic_ticker(ticker):
                logger.info(f"Skip conversion for non-alphabetic ticker: {ticker}")
                converted_files[file] = file
                continue
            original_currency = self.identify_currency(ticker)
            
            if original_currency == target_currency:
                # 通貨換算不要
                converted_files[file] = file
                continue
            
            # データを読み込み
            df = pd.read_csv(file_path)
            
            # 特殊なCSV構造に対応（最初の2行をスキップしてDateカラムを設定）
            if 'Date' not in df.columns and len(df.columns) >= 6:
                # 3行目以降のデータを使用し、最初の列をDateとして設定
                df = df.iloc[2:].reset_index(drop=True)
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                
                # 空のDate行を削除
                df = df.dropna(subset=['Date'])
                df = df[df['Date'] != '']
                
                # 数値列を数値型に変換
                for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 通貨換算
            converted_df = self.convert_currency(df, original_currency, target_currency, exchange_rates)
            
            # 換算済みファイル名を生成
            converted_filename = f"{ticker}_{target_currency}.csv"
            converted_file_path = os.path.join(self.analysis_dir, converted_filename)
            
            # 保存
            converted_df.to_csv(converted_file_path, index=False)
            converted_files[file] = converted_filename
            
            logger.info(f"Converted {file} from {original_currency} to {target_currency}")
        
        # メタデータを保存
        self._save_metadata(files, converted_files, target_currency)
        
        return converted_files
    
    def _save_metadata(self, original_files: List[str], converted_files: Dict[str, str], 
                      target_currency: str):
        """
        変換メタデータを保存
        """
        metadata = {
            'conversion_date': datetime.now().isoformat(),
            'target_currency': target_currency,
            'exchange_rate_file': 'USDJPY.csv',
            'conversions': converted_files,
            'original_files': original_files
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def get_analysis_file_path(self, original_file: str, target_currency: str) -> str:
        """
        分析用ファイルのパスを取得
        """
        ticker = original_file.replace('.csv', '')
        original_currency = self.identify_currency(ticker)
        
        # 英字以外のファイル名は常に元ファイルを使用
        if not self._is_alphabetic_ticker(ticker):
            return os.path.join(self.data_dir, original_file)
        
        if original_currency == target_currency:
            # 元のファイルを使用
            return os.path.join(self.data_dir, original_file)
        else:
            # 換算済みファイルを使用
            converted_filename = f"{ticker}_{target_currency}.csv"
            converted_file_path = os.path.join(self.analysis_dir, converted_filename)
            
            # 換算済みファイルが存在しない場合は生成
            if not os.path.exists(converted_file_path):
                logger.info(f"Converting {original_file} to {target_currency}")
                self.generate_analysis_data([original_file], target_currency)
            
            return converted_file_path
    
    def ensure_analysis_data(self, files: List[str], target_currency: str) -> List[str]:
        """
        分析用データが存在することを保証し、必要なファイルパスのリストを返す
        """
        analysis_files = []
        
        for file in files:
            ticker = file.replace('.csv', '')
            original_currency = self.identify_currency(ticker)
            
            # 英字以外のファイル名は常に元ファイルを使用
            if not self._is_alphabetic_ticker(ticker):
                analysis_files.append(os.path.join(self.data_dir, file))
                continue
            
            if original_currency == target_currency:
                # 元のファイルを使用
                analysis_files.append(os.path.join(self.data_dir, file))
            else:
                # 換算済みファイルのパスを確認
                converted_filename = f"{ticker}_{target_currency}.csv"
                converted_file_path = os.path.join(self.analysis_dir, converted_filename)
                
                if not os.path.exists(converted_file_path):
                    # 換算済みファイルが存在しない場合は生成
                    self.generate_analysis_data([file], target_currency)
                
                analysis_files.append(converted_file_path)
        
        return analysis_files
