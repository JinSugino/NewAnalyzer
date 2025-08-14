// 共通モデル定義

// 日時フォーマット用のユーティリティ
class DateUtils {
  static String formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  static DateTime? parseDate(String dateString) {
    try {
      return DateTime.parse(dateString);
    } catch (e) {
      return null;
    }
  }

  static String formatDateTime(DateTime dateTime) {
    return '${dateTime.year}-${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}

// 共通パラメータ
class CommonParams {
  final String? method; // "simple" or "log"
  final bool? annualize;
  final int? periodsPerYear;
  final List<String>? tickers;

  CommonParams({
    this.method,
    this.annualize,
    this.periodsPerYear,
    this.tickers,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    if (method != null) data['method'] = method;
    if (annualize != null) data['annualize'] = annualize;
    if (periodsPerYear != null) data['periods_per_year'] = periodsPerYear;
    if (tickers != null) data['tickers'] = tickers;
    return data;
  }
}

// ファイル情報
class FileInfo {
  final String filename;
  final String filePath;
  final int sizeBytes;
  final String sizeReadable;
  final String createdTime;
  final String modifiedTime;
  final bool exists;

  FileInfo({
    required this.filename,
    required this.filePath,
    required this.sizeBytes,
    required this.sizeReadable,
    required this.createdTime,
    required this.modifiedTime,
    required this.exists,
  });

  factory FileInfo.fromJson(Map<String, dynamic> json) {
    return FileInfo(
      filename: json['filename'] ?? '',
      filePath: json['file_path'] ?? '',
      sizeBytes: json['size_bytes'] ?? 0,
      sizeReadable: json['size_readable'] ?? '',
      createdTime: json['created_time'] ?? '',
      modifiedTime: json['modified_time'] ?? '',
      exists: json['exists'] ?? false,
    );
  }
}

// 削除結果
class DeleteResult {
  final bool success;
  final List<String> deletedFiles;
  final List<String> failedFiles;
  final int totalRequested;
  final int totalDeleted;
  final int totalFailed;
  final String? error;

  DeleteResult({
    required this.success,
    required this.deletedFiles,
    required this.failedFiles,
    required this.totalRequested,
    required this.totalDeleted,
    required this.totalFailed,
    this.error,
  });

  factory DeleteResult.fromJson(Map<String, dynamic> json) {
    return DeleteResult(
      success: json['success'] ?? false,
      deletedFiles: List<String>.from(json['deleted_files'] ?? []),
      failedFiles: List<String>.from(json['failed_files'] ?? []),
      totalRequested: json['total_requested'] ?? 0,
      totalDeleted: json['total_deleted'] ?? 0,
      totalFailed: json['total_failed'] ?? 0,
      error: json['error'],
    );
  }
}

// プロバイダー情報
class ProviderInfo {
  final String name;
  final String version;
  final String description;
  final List<String> supportedSymbols;
  final Map<String, dynamic> rateLimits;
  final List<String> dataAvailable;

  ProviderInfo({
    required this.name,
    required this.version,
    required this.description,
    required this.supportedSymbols,
    required this.rateLimits,
    required this.dataAvailable,
  });

  factory ProviderInfo.fromJson(Map<String, dynamic> json) {
    return ProviderInfo(
      name: json['name'] ?? '',
      version: json['version'] ?? '',
      description: json['description'] ?? '',
      supportedSymbols: List<String>.from(json['supported_symbols'] ?? []),
      rateLimits: Map<String, dynamic>.from(json['rate_limits'] ?? {}),
      dataAvailable: List<String>.from(json['data_available'] ?? []),
    );
  }
}

// 検索結果
class SearchResult {
  final String symbol;
  final String name;
  final String exchange;
  final String type;
  final String market;

  SearchResult({
    required this.symbol,
    required this.name,
    required this.exchange,
    required this.type,
    required this.market,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    return SearchResult(
      symbol: json['symbol'] ?? '',
      name: json['name'] ?? '',
      exchange: json['exchange'] ?? '',
      type: json['type'] ?? '',
      market: json['market'] ?? '',
    );
  }
}

// 会社情報
class CompanyInfo {
  final String symbol;
  final String name;
  final String shortName;
  final String sector;
  final String industry;
  final String country;
  final String currency;
  final String exchange;
  final double? marketCap;
  final double? peRatio;
  final double? dividendYield;
  final double? beta;
  final String? website;
  final String description;

  CompanyInfo({
    required this.symbol,
    required this.name,
    required this.shortName,
    required this.sector,
    required this.industry,
    required this.country,
    required this.currency,
    required this.exchange,
    this.marketCap,
    this.peRatio,
    this.dividendYield,
    this.beta,
    this.website,
    required this.description,
  });

  factory CompanyInfo.fromJson(Map<String, dynamic> json) {
    return CompanyInfo(
      symbol: json['symbol'] ?? '',
      name: json['name'] ?? '',
      shortName: json['short_name'] ?? '',
      sector: json['sector'] ?? '',
      industry: json['industry'] ?? '',
      country: json['country'] ?? '',
      currency: json['currency'] ?? '',
      exchange: json['exchange'] ?? '',
      marketCap: json['market_cap']?.toDouble(),
      peRatio: json['pe_ratio']?.toDouble(),
      dividendYield: json['dividend_yield']?.toDouble(),
      beta: json['beta']?.toDouble(),
      website: json['website'],
      description: json['description'] ?? '',
    );
  }
}
