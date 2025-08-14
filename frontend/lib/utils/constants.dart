// アプリケーション全体で使用する定数

// API関連
class ApiConstants {
  static const String baseUrl = 'http://127.0.0.1:8000';
  static const int timeoutSeconds = 30;
  static const int retryCount = 3;
}

// チャート関連
class ChartConstants {
  static const int defaultBbWindow = 20;
  static const double defaultBbStd = 2.0;
  static const int defaultRsiPeriod = 14;
  static const int defaultMacdFast = 12;
  static const int defaultMacdSlow = 26;
  static const int defaultMacdSignal = 9;
  static const int defaultAxisTick = 10;
  static const String defaultAxisTickFormat = '%Y-%m-%d';
}

// 分析関連
class AnalysisConstants {
  static const double defaultRiskFreeRate = 0.0;
  static const int defaultPeriodsPerYear = 252;
  static const String defaultMethod = 'simple';
  static const double defaultCorrelationThreshold = 0.9;
  static const String defaultConsolidationMethod = 'mean';
}

// ポートフォリオ関連
class PortfolioConstants {
  static const bool defaultAllowShort = true;
  static const int defaultNumFrontierPoints = 50;
  static const int defaultNumSamples = 2000;
  static const double defaultMaxLeverage = 2.0;
  static const bool defaultConsolidateCorrelated = false;
}

// ダウンロード関連
class DownloadConstants {
  static const String defaultProvider = 'yahoo';
  static const String defaultInterval = '1d';
  static const bool defaultPrepost = false;
}

// UI関連
class UIConstants {
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;
  static const double borderRadius = 8.0;
  static const double buttonHeight = 48.0;
  static const double inputHeight = 56.0;
}

// 色関連
class AppColors {
  static const int primaryColor = 0xFF2196F3;
  static const int secondaryColor = 0xFF1976D2;
  static const int accentColor = 0xFF03DAC6;
  static const int errorColor = 0xFFB00020;
  static const int successColor = 0xFF4CAF50;
  static const int warningColor = 0xFFFF9800;
  static const int backgroundColor = 0xFFF5F5F5;
  static const int surfaceColor = 0xFFFFFFFF;
  static const int textColor = 0xFF212121;
  static const int textSecondaryColor = 0xFF757575;
}

// テキストスタイル
class TextStyles {
  static const double headline1Size = 24.0;
  static const double headline2Size = 20.0;
  static const double headline3Size = 18.0;
  static const double body1Size = 16.0;
  static const double body2Size = 14.0;
  static const double captionSize = 12.0;
}

// アニメーション関連
class AnimationConstants {
  static const Duration shortDuration = Duration(milliseconds: 200);
  static const Duration mediumDuration = Duration(milliseconds: 300);
  static const Duration longDuration = Duration(milliseconds: 500);
}

// エラーメッセージ
class ErrorMessages {
  static const String networkError = 'ネットワークエラーが発生しました';
  static const String serverError = 'サーバーエラーが発生しました';
  static const String invalidInput = '入力が無効です';
  static const String fileNotFound = 'ファイルが見つかりません';
  static const String downloadFailed = 'ダウンロードに失敗しました';
  static const String analysisFailed = '分析に失敗しました';
  static const String portfolioFailed = 'ポートフォリオ計算に失敗しました';
}

// 成功メッセージ
class SuccessMessages {
  static const String downloadSuccess = 'ダウンロードが完了しました';
  static const String analysisSuccess = '分析が完了しました';
  static const String portfolioSuccess = 'ポートフォリオ計算が完了しました';
  static const String fileDeleted = 'ファイルが削除されました';
}

// 検証関連
class ValidationConstants {
  static const int minSymbolLength = 1;
  static const int maxSymbolLength = 20;
  static const double minRiskFreeRate = -1.0;
  static const double maxRiskFreeRate = 1.0;
  static const int minPeriodsPerYear = 1;
  static const int maxPeriodsPerYear = 365;
  static const double minCorrelationThreshold = 0.0;
  static const double maxCorrelationThreshold = 1.0;
}

// ファイル関連
class FileConstants {
  static const List<String> supportedExtensions = ['.csv'];
  static const int maxFileSizeMB = 100;
  static const String defaultDateFormat = 'yyyy-MM-dd';
  static const String defaultDateTimeFormat = 'yyyy-MM-dd HH:mm:ss';
}

// プロバイダー関連
class ProviderConstants {
  static const List<String> availableProviders = ['yahoo'];
  static const Map<String, String> providerNames = {
    'yahoo': 'Yahoo Finance',
  };
  static const Map<String, String> providerDescriptions = {
    'yahoo': 'Yahoo Financeから株価データを取得',
  };
}
