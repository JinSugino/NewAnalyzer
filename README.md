# NewAnalyzer

株価分析とポートフォリオ最適化のためのWebアプリケーション

## 🚀 クイックスタート

### 1. リポジトリのクローン
```bash
git clone https://github.com/JinSugino/NewAnalyzer.git
cd NewAnalyzer
```

### 2. 自動セットアップ
```bash
python setup.py
```

### 3. 手動セットアップ（推奨）

#### バックエンド
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### フロントエンド
```bash
cd frontend
flutter pub get
flutter run -d chrome
```

## 📋 システム要件

- Python 3.8+
- Flutter 3.0+
- Node.js 16+ (オプション)

## 🔧 依存関係

### バックエンド
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pandas 2.1.3
- Plotly 5.17.0
- SciPy 1.11.4
- yfinance 0.2.28
- NumPy 1.24.3

### フロントエンド
- Flutter 3.0+
- syncfusion_flutter_charts

## 📊 機能

### チャート機能
- ローソク足チャート
- テクニカル指標
- インタラクティブチャート

### 分析機能
- 統計サマリー
- 相関分析
- 統合相関分析

### ポートフォリオ機能
- ポートフォリオ最適化
- 効率的フロンティア
- リスク・リターン分析

### ダウンロード機能
- 株価データダウンロード
- 複数プロバイダー対応
- バッチダウンロード

### 通貨機能
- 円・ドル表記切替
- 為替レート自動取得
- 通貨換算対応
- 分析用データ自動生成

## 🌐 API エンドポイント

### 健康チェック
- `GET /health` - サーバー状態確認

### チャート
- `GET /chart/candlestick/{filename}` - ローソク足チャートデータ取得
- `GET /chart/html/{filename}` - HTMLチャート表示
- `GET /chart/json/{filename}` - JSON形式チャートデータ
- `GET /chart/available-files` - 利用可能ファイル一覧
- `GET /chart/file-info/{filename}` - ファイル情報取得

### ダウンロード
- `POST /download/` - データダウンロード
- `GET /download/providers` - プロバイダー一覧
- `GET /download/provider/{provider_name}/info` - プロバイダー詳細情報
- `GET /download/search` - シンボル検索
- `GET /download/company/{symbol}` - 企業情報取得
- `GET /download/files` - ダウンロード済みファイル一覧
- `GET /download/files/{filename}/info` - ファイル詳細情報
- `GET /download/files/info` - 全ファイル情報一括取得
- `GET /download/validate/{symbol}` - シンボル検証

### 通貨
- `POST /currency/download-exchange-rate` - 為替レートダウンロード
- `POST /currency/convert` - 通貨換算実行
- `GET /currency/exchange-rate-status` - 為替レート状態確認

### 分析
- `POST /analysis/summary` - 統計サマリー分析
- `POST /analysis/summary/html` - 統計サマリー分析HTML表示
- `POST /analysis/correlation` - 相関分析
- `POST /analysis/correlation/html` - 相関分析HTML表示
- `POST /analysis/consolidated-correlation` - 統合相関分析
- `POST /analysis/consolidated-correlation/html` - 統合相関分析HTML表示

### ポートフォリオ
- `POST /portfolio/optimization` - ポートフォリオ最適化
- `POST /portfolio/optimization/html` - ポートフォリオ最適化HTML表示
- `POST /portfolio/efficient-frontier` - 効率的フロンティア
- `POST /portfolio/efficient-frontier/html` - 効率的フロンティアHTML表示

## 🐛 トラブルシューティング

### チャートが表示されない
1. データファイルが存在するか確認
2. バックエンドサーバーが起動しているか確認
3. ブラウザのコンソールでエラーを確認

### 分析機能が動作しない
1. 必要なデータファイルがダウンロードされているか確認
2. 複数のティッカーを指定しているか確認
3. バックエンドのログを確認

### ポートフォリオ機能が動作しない
1. 最低2つ以上のティッカーを指定
2. データの期間が十分か確認
3. パラメータ設定を確認

### 通貨機能の使用方法

#### 1. 為替レートのダウンロード
```bash
curl -X POST "http://localhost:8000/currency/download-exchange-rate"
```

#### 2. 通貨換算の実行
```bash
curl -X POST "http://localhost:8000/currency/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["AAPL.csv", "7203.T.csv"],
    "target_currency": "JPY"
  }'
```

#### 3. 分析APIでの通貨指定
```bash
curl -X POST "http://localhost:8000/analysis/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "7203.T"],
    "currency": "JPY"
  }'
```

#### 4. チャートAPIでの通貨指定
```bash
curl "http://localhost:8000/chart/candlestick/AAPL.csv?currency=JPY"
```

#### 5. ポートフォリオAPIでの通貨指定
```bash
curl -X POST "http://localhost:8000/portfolio/optimization" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "7203.T"],
    "currency": "JPY"
  }'
```

## 📁 プロジェクト構造

```
NewAnalyzer/
├── backend/
│   ├── api/
│   ├── data/
│   ├── services/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── lib/
│   ├── pubspec.yaml
│   └── ...
├── setup.py
└── README.md
```

## 🤝 貢献

1. フォークを作成
2. フィーチャーブランチを作成
3. 変更をコミット
4. プルリクエストを作成

## 📄 ライセンス

MIT License

## 📞 サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。
