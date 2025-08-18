#!/usr/bin/env python3
"""
通貨換算スクリプト
data/のCSVファイルを読み込み、為替レートを適用してdata_analysis/に保存
"""

import pandas as pd
import os
import json
from datetime import datetime

def load_exchange_rate():
    """為替レートデータを読み込み"""
    exchange_file = "data/USDJPY.csv"
    if not os.path.exists(exchange_file):
        print(f"為替レートファイルが見つかりません: {exchange_file}")
        return None
    
    df = pd.read_csv(exchange_file)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def identify_currency(ticker):
    """ティッカーから通貨を識別"""
    if ticker.endswith('.T'):
        return 'JPY'
    else:
        return 'USD'

def convert_stock_data(df, from_currency, to_currency, exchange_rates):
    """株価データを通貨換算"""
    if from_currency == to_currency:
        return df.copy()
    
    # 為替レートとマージ
    merged = pd.merge(df, exchange_rates[['Date', 'Close']], on='Date', how='left', suffixes=('', '_rate'))
    
    # 為替レートの欠損値を削除
    merged = merged.dropna(subset=['Close_rate'])
    
    # 通貨換算
    if from_currency == 'USD' and to_currency == 'JPY':
        # ドルから円
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in merged.columns:
                merged[col] = merged[col].astype(float) * merged['Close_rate'].astype(float)
    elif from_currency == 'JPY' and to_currency == 'USD':
        # 円からドル
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in merged.columns:
                merged[col] = merged[col].astype(float) / merged['Close_rate'].astype(float)
    
    # 為替レート列を削除
    merged = merged.drop('Close_rate', axis=1)
    return merged

def process_csv_file(file_path, exchange_rates):
    """CSVファイルを処理して換算"""
    print(f"処理中: {file_path}")
    
    # ティッカーを抽出（英字以外はスキップ）
    filename = os.path.basename(file_path)
    ticker = filename.replace('.csv', '')
    if not ticker.isalpha():
        print(f"  スキップ: 英字ではないため変換しません -> {ticker}")
        return {}
    
    # ファイルを読み込み
    df = pd.read_csv(file_path)
    
    # 特殊なCSV構造に対応（最初の2行をスキップ）
    if 'Date' not in df.columns and len(df.columns) >= 6:
        df = df.iloc[2:].reset_index(drop=True)
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # 空のDate行を削除
        df = df.dropna(subset=['Date'])
        df = df[df['Date'] != '']
    
    # 数値列を確実に数値型に変換
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 欠損値を削除
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
    
    df['Date'] = pd.to_datetime(df['Date'])
    
    original_currency = identify_currency(ticker)
    
    print(f"  ティッカー: {ticker}, 元通貨: {original_currency}")
    print(f"  データ行数: {len(df)}")
    
    results = {}
    
    # USD換算
    if original_currency != 'USD':
        print(f"  USDに換算中...")
        usd_df = convert_stock_data(df, original_currency, 'USD', exchange_rates)
        usd_filename = f"{ticker}_USD.csv"
        usd_path = os.path.join("data_analysis", usd_filename)
        usd_df.to_csv(usd_path, index=False)
        results['USD'] = usd_filename
        print(f"  保存: {usd_path}")
    
    # JPY換算
    if original_currency != 'JPY':
        print(f"  JPYに換算中...")
        jpy_df = convert_stock_data(df, original_currency, 'JPY', exchange_rates)
        jpy_filename = f"{ticker}_JPY.csv"
        jpy_path = os.path.join("data_analysis", jpy_filename)
        jpy_df.to_csv(jpy_path, index=False)
        results['JPY'] = jpy_filename
        print(f"  保存: {jpy_path}")
    
    return results

def main():
    """メイン処理"""
    print("=== 通貨換算スクリプト ===")
    
    # ディレクトリ確認
    if not os.path.exists("data"):
        print("dataディレクトリが見つかりません")
        return
    
    if not os.path.exists("data_analysis"):
        os.makedirs("data_analysis")
        print("data_analysisディレクトリを作成しました")
    
    # 為替レート読み込み
    print("為替レートを読み込み中...")
    exchange_rates = load_exchange_rate()
    if exchange_rates is None:
        return
    
    print(f"為替レート期間: {exchange_rates['Date'].min()} ～ {exchange_rates['Date'].max()}")
    
    # CSVファイル一覧
    csv_files = [f for f in os.listdir("data") if f.endswith('.csv') and f != 'USDJPY.csv']
    print(f"処理対象ファイル: {csv_files}")
    
    # 各ファイルを処理
    all_conversions = {}
    for csv_file in csv_files:
        file_path = os.path.join("data", csv_file)
        conversions = process_csv_file(file_path, exchange_rates)
        all_conversions[csv_file] = conversions
    
    # メタデータ保存
    metadata = {
        'conversion_date': datetime.now().isoformat(),
        'exchange_rate_file': 'USDJPY.csv',
        'conversions': all_conversions,
        'original_files': csv_files
    }
    
    metadata_path = os.path.join("data_analysis", "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\nメタデータ保存: {metadata_path}")
    print("=== 換算完了 ===")
    
    # 結果表示
    print("\n生成されたファイル:")
    for file in os.listdir("data_analysis"):
        if file.endswith('.csv'):
            print(f"  {file}")

if __name__ == "__main__":
    main()
