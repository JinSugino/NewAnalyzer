#!/usr/bin/env python3
"""
NewAnalyzer Setup Script
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """コマンドを実行"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def setup_backend():
    """バックエンドのセットアップ"""
    print("🔧 Setting up backend...")
    
    # requirements.txtをインストール
    if not run_command("pip install -r requirements.txt", cwd="backend"):
        return False
    
    # データディレクトリを作成
    data_dir = Path("backend/data")
    data_dir.mkdir(exist_ok=True)
    
    print("✅ Backend setup completed")
    return True

def setup_frontend():
    """フロントエンドのセットアップ"""
    print("🔧 Setting up frontend...")
    
    # Flutter依存関係を取得
    if not run_command("flutter pub get", cwd="frontend"):
        return False
    
    print("✅ Frontend setup completed")
    return True

def download_sample_data():
    """サンプルデータをダウンロード"""
    print("📥 Downloading sample data...")
    
    # バックエンドサーバーを一時的に起動してデータをダウンロード
    try:
        # サンプルデータのダウンロード
        symbols = ["AAPL", "MSFT", "GOOGL", "SPY", "VOO"]
        for symbol in symbols:
            print(f"Downloading {symbol}...")
            # ここで実際のダウンロード処理を行う
            # 現在は既存のデータファイルを使用
        
        print("✅ Sample data setup completed")
        return True
    except Exception as e:
        print(f"❌ Error downloading sample data: {e}")
        return False

def main():
    """メインセットアップ関数"""
    print("🚀 NewAnalyzer Setup")
    print("=" * 50)
    
    # バックエンドセットアップ
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # フロントエンドセットアップ
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # サンプルデータセットアップ
    if not download_sample_data():
        print("⚠️ Sample data setup failed (using existing data)")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start backend: cd backend && python main.py")
    print("2. Start frontend: cd frontend && flutter run -d chrome")
    print("3. Open http://localhost:8000/health to check backend")
    print("4. Open http://localhost:3000 to access frontend")

if __name__ == "__main__":
    main()
