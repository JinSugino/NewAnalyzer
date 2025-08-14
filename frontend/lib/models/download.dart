// ダウンロード関連のモデル定義
import 'common.dart';

// ダウンロードパラメータ
class DownloadParams {
  final String symbol;
  final String providerName;
  final String? startDate;
  final String? endDate;
  final String? filename;
  final String interval;
  final bool prepost;

  DownloadParams({
    required this.symbol,
    this.providerName = 'yahoo',
    this.startDate,
    this.endDate,
    this.filename,
    this.interval = '1d',
    this.prepost = false,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'symbol': symbol,
      'provider_name': providerName,
      'interval': interval,
      'prepost': prepost,
    };
    
    if (startDate != null) {
      data['start_date'] = startDate;
    }
    if (endDate != null) {
      data['end_date'] = endDate;
    }
    if (filename != null) {
      data['filename'] = filename;
    }
    
    return data;
  }
}

// 一括ダウンロードパラメータ
class BatchDownloadParams {
  final List<String> symbols;
  final String providerName;
  final String? startDate;
  final String? endDate;
  final String interval;
  final bool prepost;

  BatchDownloadParams({
    required this.symbols,
    this.providerName = 'yahoo',
    this.startDate,
    this.endDate,
    this.interval = '1d',
    this.prepost = false,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'symbols': symbols,
      'provider_name': providerName,
      'interval': interval,
      'prepost': prepost,
    };
    
    if (startDate != null) {
      data['start_date'] = startDate;
    }
    if (endDate != null) {
      data['end_date'] = endDate;
    }
    
    return data;
  }
}

// ダウンロード結果
class DownloadResult {
  final bool success;
  final String symbol;
  final String provider;
  final String? filePath;
  final int? dataPoints;
  final Map<String, dynamic>? metadata;
  final String? error;

  DownloadResult({
    required this.success,
    required this.symbol,
    required this.provider,
    this.filePath,
    this.dataPoints,
    this.metadata,
    this.error,
  });

  factory DownloadResult.fromJson(Map<String, dynamic> json) {
    return DownloadResult(
      success: json['success'] ?? false,
      symbol: json['symbol'] ?? '',
      provider: json['provider'] ?? '',
      filePath: json['file_path'],
      dataPoints: json['data_points'],
      metadata: json['metadata'] != null
          ? Map<String, dynamic>.from(json['metadata'])
          : null,
      error: json['error'],
    );
  }
}

// 一括ダウンロード結果
class BatchDownloadResult {
  final int total;
  final int successCount;
  final int failedCount;
  final List<DownloadResult> success;
  final List<Map<String, dynamic>> failed;

  BatchDownloadResult({
    required this.total,
    required this.successCount,
    required this.failedCount,
    required this.success,
    required this.failed,
  });

  factory BatchDownloadResult.fromJson(Map<String, dynamic> json) {
    return BatchDownloadResult(
      total: json['total'] ?? 0,
      successCount: json['success_count'] ?? 0,
      failedCount: json['failed_count'] ?? 0,
      success: (json['success'] as List?)
          ?.map((item) => DownloadResult.fromJson(item))
          .toList() ?? [],
      failed: (json['failed'] as List?)
          ?.map((item) => Map<String, dynamic>.from(item))
          .toList() ?? [],
    );
  }
}

// プロバイダー情報
class DownloadProviderInfo {
  final List<String> availableProviders;
  final Map<String, ProviderInfo> providerInfo;

  DownloadProviderInfo({
    required this.availableProviders,
    required this.providerInfo,
  });

  factory DownloadProviderInfo.fromJson(Map<String, dynamic> json) {
    final providerInfoData = Map<String, dynamic>.from(json['provider_info'] ?? {});
    final providerInfo = <String, ProviderInfo>{};
    
    providerInfoData.forEach((key, value) {
      if (value is Map<String, dynamic>) {
        providerInfo[key] = ProviderInfo.fromJson(value);
      }
    });

    return DownloadProviderInfo(
      availableProviders: List<String>.from(json['available_providers'] ?? []),
      providerInfo: providerInfo,
    );
  }
}

// 検索結果
class SearchResults {
  final String query;
  final String provider;
  final List<SearchResult> results;
  final int count;

  SearchResults({
    required this.query,
    required this.provider,
    required this.results,
    required this.count,
  });

  factory SearchResults.fromJson(Map<String, dynamic> json) {
    return SearchResults(
      query: json['query'] ?? '',
      provider: json['provider'] ?? '',
      results: (json['results'] as List?)
          ?.map((item) => SearchResult.fromJson(item))
          .toList() ?? [],
      count: json['count'] ?? 0,
    );
  }
}

// ファイル一覧
class FileList {
  final List<String> files;
  final int count;

  FileList({
    required this.files,
    required this.count,
  });

  factory FileList.fromJson(Map<String, dynamic> json) {
    return FileList(
      files: List<String>.from(json['files'] ?? []),
      count: json['count'] ?? 0,
    );
  }
}

// 全ファイル情報
class AllFilesInfo {
  final List<FileInfo> files;
  final int count;
  final int totalSizeBytes;
  final String totalSizeReadable;

  AllFilesInfo({
    required this.files,
    required this.count,
    required this.totalSizeBytes,
    required this.totalSizeReadable,
  });

  factory AllFilesInfo.fromJson(Map<String, dynamic> json) {
    return AllFilesInfo(
      files: (json['files'] as List?)
          ?.map((item) => FileInfo.fromJson(item))
          .toList() ?? [],
      count: json['count'] ?? 0,
      totalSizeBytes: json['total_size_bytes'] ?? 0,
      totalSizeReadable: json['total_size_readable'] ?? '',
    );
  }
}

// シンボル検証結果
class SymbolValidationResult {
  final String symbol;
  final String provider;
  final bool isValid;

  SymbolValidationResult({
    required this.symbol,
    required this.provider,
    required this.isValid,
  });

  factory SymbolValidationResult.fromJson(Map<String, dynamic> json) {
    return SymbolValidationResult(
      symbol: json['symbol'] ?? '',
      provider: json['provider'] ?? '',
      isValid: json['is_valid'] ?? false,
    );
  }
}
