import '../models/download.dart';
import '../models/common.dart';
import 'api_client.dart';

class DownloadApi {
  // プロバイダー一覧を取得
  static Future<ApiResponse<DownloadProviderInfo>> getProviders() async {
    return await ApiClient.get<DownloadProviderInfo>(
      '/download/providers',
      fromJson: (json) => DownloadProviderInfo.fromJson(json),
    );
  }

  // プロバイダー情報を取得
  static Future<ApiResponse<ProviderInfo>> getProviderInfo(String providerName) async {
    return await ApiClient.get<ProviderInfo>(
      '/download/provider/$providerName/info',
      fromJson: (json) => ProviderInfo.fromJson(json),
    );
  }

  // シンボルを検索
  static Future<ApiResponse<SearchResults>> searchSymbols(
    String query,
    String providerName,
  ) async {
    return await ApiClient.get<SearchResults>(
      '/download/search',
      queryParameters: {
        'query': query,
        'provider_name': providerName,
      },
      fromJson: (json) => SearchResults.fromJson(json),
    );
  }

  // 会社情報を取得
  static Future<ApiResponse<CompanyInfo>> getCompanyInfo(
    String symbol,
    String providerName,
  ) async {
    return await ApiClient.get<CompanyInfo>(
      '/download/company/$symbol',
      queryParameters: {
        'provider_name': providerName,
      },
      fromJson: (json) => CompanyInfo.fromJson(json),
    );
  }

  // 株価データをダウンロード
  static Future<ApiResponse<DownloadResult>> downloadStockData(
    DownloadParams params,
  ) async {
    return await ApiClient.post<DownloadResult>(
      '/download/download',
      queryParameters: params.toJson(),
      fromJson: (json) => DownloadResult.fromJson(json),
    );
  }

  // 一括ダウンロード
  static Future<ApiResponse<BatchDownloadResult>> batchDownload(
    BatchDownloadParams params,
  ) async {
    return await ApiClient.post<BatchDownloadResult>(
      '/download/batch-download',
      queryParameters: params.toJson(),
      fromJson: (json) => BatchDownloadResult.fromJson(json),
    );
  }

  // ファイル一覧を取得
  static Future<ApiResponse<FileList>> getFiles() async {
    return await ApiClient.get<FileList>(
      '/download/files',
      fromJson: (json) => FileList.fromJson(json),
    );
  }

  // 全ファイル情報を取得
  static Future<ApiResponse<AllFilesInfo>> getAllFilesInfo() async {
    return await ApiClient.get<AllFilesInfo>(
      '/download/files/info',
      fromJson: (json) => AllFilesInfo.fromJson(json),
    );
  }

  // ファイル情報を取得
  static Future<ApiResponse<FileInfo>> getFileInfo(String filename) async {
    return await ApiClient.get<FileInfo>(
      '/download/files/$filename/info',
      fromJson: (json) => FileInfo.fromJson(json),
    );
  }

  // ファイルを削除
  static Future<ApiResponse<Map<String, dynamic>>> deleteFile(String filename) async {
    return await ApiClient.delete<Map<String, dynamic>>(
      '/download/files/$filename',
      fromJson: (json) => Map<String, dynamic>.from(json),
    );
  }

  // シンボル関連ファイルを削除
  static Future<ApiResponse<DeleteResult>> deleteFilesBySymbol(String symbol) async {
    return await ApiClient.delete<DeleteResult>(
      '/download/files/symbol/$symbol',
      fromJson: (json) => DeleteResult.fromJson(json),
    );
  }

  // 複数ファイルを一括削除
  static Future<ApiResponse<DeleteResult>> deleteMultipleFiles(List<String> filenames) async {
    return await ApiClient.delete<DeleteResult>(
      '/download/files/batch',
      queryParameters: {
        'filenames': filenames,
      },
      fromJson: (json) => DeleteResult.fromJson(json),
    );
  }

  // 全ファイルを削除
  static Future<ApiResponse<DeleteResult>> deleteAllFiles() async {
    return await ApiClient.delete<DeleteResult>(
      '/download/files/all',
      fromJson: (json) => DeleteResult.fromJson(json),
    );
  }

  // シンボルを検証
  static Future<ApiResponse<SymbolValidationResult>> validateSymbol(
    String symbol,
    String providerName,
  ) async {
    return await ApiClient.get<SymbolValidationResult>(
      '/download/validate/$symbol',
      queryParameters: {
        'provider_name': providerName,
      },
      fromJson: (json) => SymbolValidationResult.fromJson(json),
    );
  }
}
