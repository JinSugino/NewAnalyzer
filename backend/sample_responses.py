#!/usr/bin/env python3
"""
デバッグ用
サンプルエンドポイント応答生成スクリプト
各APIエンドポイントの応答例をJSON形式で生成し、実行内容を記録
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

class SampleResponseGenerator:
    """サンプル応答生成クラス"""
    
    def __init__(self):
        self.output_dir = "sample_responses"
        os.makedirs(self.output_dir, exist_ok=True)
        self.execution_log = []
    
    def log_execution(self, endpoint: str, params: Dict[str, Any], response_type: str):
        """実行内容をログに記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "parameters": params,
            "response_type": response_type
        }
        self.execution_log.append(log_entry)
        
        # ログファイルに保存
        log_file = os.path.join(self.output_dir, "execution_log.json")
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.execution_log, f, indent=2, ensure_ascii=False)
    
    def generate_chart_response(self, ticker: str, currency: str = "USD", with_indicators: bool = True):
        """チャート応答サンプル生成"""
        response = {
            "ticker": ticker,
            "currency": currency,
            "with_indicators": with_indicators,
            "data": {
                "dates": ["2020-01-01", "2020-01-02", "2020-01-03"],
                "open": [100.0, 101.0, 102.0] if currency == "USD" else [15000.0, 15150.0, 15300.0],
                "high": [102.0, 103.0, 104.0] if currency == "USD" else [15300.0, 15450.0, 15600.0],
                "low": [99.0, 100.0, 101.0] if currency == "USD" else [14850.0, 15000.0, 15150.0],
                "close": [101.0, 102.0, 103.0] if currency == "USD" else [15150.0, 15300.0, 15450.0],
                "volume": [1000000, 1100000, 1200000]
            },
            "indicators": {
                "sma_20": [100.5, 100.7, 100.9] if currency == "USD" else [15075.0, 15105.0, 15135.0],
                "sma_50": [100.2, 100.3, 100.4] if currency == "USD" else [15030.0, 15045.0, 15060.0]
            } if with_indicators else None,
            "metadata": {
                "currency_converted": currency != "USD",
                "exchange_rate_used": 150.0 if currency == "JPY" else 1.0,
                "data_source": "data_analysis" if ticker in ["SPY", "MSFT"] else "data"
            }
        }
        
        filename = f"chart_{ticker}_{currency}.json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        self.log_execution(f"/chart/html/{ticker}.csv", 
                          {"currency": currency, "with_indicators": with_indicators}, 
                          "chart_response")
        
        return response
    
    def generate_correlation_response(self, tickers: List[str] = None):
        """相関分析応答サンプル生成（円換算固定）"""
        if tickers is None:
            tickers = ["SPY", "MSFT", "7203", "9984"]
        
        # 円換算後の価格で相関計算
        response = {
            "currency": "JPY",  # 固定
            "tickers": tickers,
            "correlation_matrix": {
                "SPY": {"SPY": 1.0, "MSFT": 0.85, "7203": 0.45, "9984": 0.42},
                "MSFT": {"SPY": 0.85, "MSFT": 1.0, "7203": 0.48, "9984": 0.44},
                "7203": {"SPY": 0.45, "MSFT": 0.48, "7203": 1.0, "9984": 0.92},
                "9984": {"SPY": 0.42, "MSFT": 0.44, "7203": 0.92, "9984": 1.0}
            },
            "metadata": {
                "currency_converted": True,
                "exchange_rate_used": 150.0,
                "data_sources": {
                    "SPY": "data_analysis/SPY_JPY.csv",
                    "MSFT": "data_analysis/MSFT_JPY.csv", 
                    "7203": "data/7203.csv",
                    "9984": "data/9984.csv"
                }
            }
        }
        
        filename = "correlation_analysis_jpy.json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        self.log_execution("/analysis/correlation/html", 
                          {"currency": "JPY", "tickers": tickers}, 
                          "correlation_response")
        
        return response
    
    def generate_consolidated_correlation_response(self, correlation_threshold: float = 0.9):
        """相関統合分析応答サンプル生成（円換算固定）"""
        response = {
            "currency": "JPY",  # 固定
            "correlation_threshold": correlation_threshold,
            "consolidation_method": "mean",
            "original_correlation": {
                "SPY": {"SPY": 1.0, "MSFT": 0.85, "7203": 0.45, "9984": 0.42},
                "MSFT": {"SPY": 0.85, "MSFT": 1.0, "7203": 0.48, "9984": 0.44},
                "7203": {"SPY": 0.45, "MSFT": 0.48, "7203": 1.0, "9984": 0.92},
                "9984": {"SPY": 0.42, "MSFT": 0.44, "7203": 0.92, "9984": 1.0}
            },
            "consolidated_correlation": {
                "SPY": {"SPY": 1.0, "MSFT": 0.85, "7203+9984": 0.44},
                "MSFT": {"SPY": 0.85, "MSFT": 1.0, "7203+9984": 0.46},
                "7203+9984": {"SPY": 0.44, "MSFT": 0.46, "7203+9984": 1.0}
            },
            "consolidation_groups": [
                ["7203", "9984"]  # 相関0.92で統合
            ],
            "metadata": {
                "currency_converted": True,
                "exchange_rate_used": 150.0,
                "original_assets": 4,
                "consolidated_assets": 3
            }
        }
        
        filename = "consolidated_correlation_jpy.json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        self.log_execution("/analysis/consolidated-correlation/html", 
                          {"currency": "JPY", "correlation_threshold": correlation_threshold}, 
                          "consolidated_correlation_response")
        
        return response
    
    def generate_statistics_response(self, tickers: List[str] = None):
        """統計分析応答サンプル生成（円換算固定）"""
        if tickers is None:
            tickers = ["SPY", "MSFT", "7203", "9984"]
        
        response = {
            "currency": "JPY",  # 固定
            "tickers": tickers,
            "statistics": {
                "SPY": {
                    "mean_return_daily": 0.0008,
                    "volatility_daily": 0.015,
                    "sharpe_daily": 0.053,
                    "mean_return_annual": 0.20,
                    "volatility_annual": 0.24,
                    "sharpe_annual": 0.83,
                    "observations": 1255
                },
                "MSFT": {
                    "mean_return_daily": 0.0012,
                    "volatility_daily": 0.018,
                    "sharpe_daily": 0.067,
                    "mean_return_annual": 0.30,
                    "volatility_annual": 0.29,
                    "sharpe_annual": 1.03,
                    "observations": 1255
                },
                "7203": {
                    "mean_return_daily": 0.0006,
                    "volatility_daily": 0.020,
                    "sharpe_daily": 0.030,
                    "mean_return_annual": 0.15,
                    "volatility_annual": 0.32,
                    "sharpe_annual": 0.47,
                    "observations": 1255
                },
                "9984": {
                    "mean_return_daily": 0.0007,
                    "volatility_daily": 0.022,
                    "sharpe_daily": 0.032,
                    "mean_return_annual": 0.18,
                    "volatility_annual": 0.35,
                    "sharpe_annual": 0.51,
                    "observations": 1255
                }
            },
            "metadata": {
                "currency_converted": True,
                "exchange_rate_used": 150.0,
                "data_sources": {
                    "SPY": "data_analysis/SPY_JPY.csv",
                    "MSFT": "data_analysis/MSFT_JPY.csv",
                    "7203": "data/7203.csv",
                    "9984": "data/9984.csv"
                }
            }
        }
        
        filename = "statistics_analysis_jpy.json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        self.log_execution("/analysis/summary/html", 
                          {"currency": "JPY", "tickers": tickers}, 
                          "statistics_response")
        
        return response
    
    def generate_portfolio_response(self, tickers: List[str] = None, consolidate_correlated: bool = True):
        """ポートフォリオ最適化応答サンプル生成（円換算固定）"""
        if tickers is None:
            tickers = ["SPY", "MSFT", "7203", "9984"]
        
        response = {
            "currency": "JPY",  # 固定
            "tickers": tickers,
            "consolidate_correlated": consolidate_correlated,
            "optimization_method": "sharpe",
            "allow_short": True,
            "efficient_frontier": {
                "risks": [0.20, 0.25, 0.30, 0.35, 0.40],
                "returns": [0.15, 0.20, 0.25, 0.30, 0.35]
            },
            "optimal_portfolio": {
                "weights": {
                    "SPY": 0.35,
                    "MSFT": 0.45,
                    "7203+9984": 0.20  # 統合後
                } if consolidate_correlated else {
                    "SPY": 0.30,
                    "MSFT": 0.40,
                    "7203": 0.15,
                    "9984": 0.15
                },
                "expected_return": 0.25,
                "expected_risk": 0.28,
                "sharpe_ratio": 0.89
            },
            "metadata": {
                "currency_converted": True,
                "exchange_rate_used": 150.0,
                "data_sources": {
                    "SPY": "data_analysis/SPY_JPY.csv",
                    "MSFT": "data_analysis/MSFT_JPY.csv",
                    "7203": "data/7203.csv",
                    "9984": "data/9984.csv"
                },
                "consolidation_groups": [["7203", "9984"]] if consolidate_correlated else []
            }
        }
        
        filename = "portfolio_optimization_jpy.json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        self.log_execution("/portfolio/optimization/html", 
                          {"currency": "JPY", "consolidate_correlated": consolidate_correlated, "tickers": tickers}, 
                          "portfolio_response")
        
        return response
    
    def generate_all_samples(self):
        """すべてのサンプル応答を生成"""
        print("=== サンプル応答生成開始 ===")
        
        # チャート応答（円・ドル選択可能）
        print("1. チャート応答生成中...")
        self.generate_chart_response("SPY", "USD", True)
        self.generate_chart_response("SPY", "JPY", True)
        self.generate_chart_response("7203", "JPY", False)
        
        # 相関分析応答（円換算固定）
        print("2. 相関分析応答生成中...")
        self.generate_correlation_response()
        
        # 相関統合分析応答（円換算固定）
        print("3. 相関統合分析応答生成中...")
        self.generate_consolidated_correlation_response()
        
        # 統計分析応答（円換算固定）
        print("4. 統計分析応答生成中...")
        self.generate_statistics_response()
        
        # ポートフォリオ最適化応答（円換算固定）
        print("5. ポートフォリオ最適化応答生成中...")
        self.generate_portfolio_response(consolidate_correlated=True)
        self.generate_portfolio_response(consolidate_correlated=False)
        
        print(f"=== サンプル応答生成完了 ===")
        print(f"出力ディレクトリ: {self.output_dir}")
        print(f"実行ログ: {self.output_dir}/execution_log.json")
        
        # 生成されたファイル一覧を表示
        files = os.listdir(self.output_dir)
        print("\n生成されたファイル:")
        for file in sorted(files):
            print(f"  {file}")

def main():
    """メイン処理"""
    generator = SampleResponseGenerator()
    generator.generate_all_samples()

if __name__ == "__main__":
    main()
