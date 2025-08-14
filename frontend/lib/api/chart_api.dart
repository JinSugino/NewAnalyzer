import 'package:http/http.dart' as http;
import '../models/chart.dart';
import 'api_client.dart';

class ChartApi {
  // ローソク足チャートを取得
  static Future<ApiResponse<ChartDataLegacy>> getCandlestickChart(
    String filename,
    ChartParams params,
  ) async {
    return await ApiClient.get<ChartDataLegacy>(
      '/chart/candlestick/$filename',
      queryParameters: params.toJson(),
      fromJson: (json) => ChartDataLegacy.fromJson(json),
    );
  }

  // JSONチャートデータを取得
  static Future<ApiResponse<Map<String, dynamic>>> getJsonChart(
    String filename,
    ChartParams params,
  ) async {
    return await ApiClient.get<Map<String, dynamic>>(
      '/chart/json/$filename',
      queryParameters: params.toJson(),
    );
  }

  // HTMLチャートを取得
  static Future<ApiResponse<String>> getHtmlChart(
    String filename,
    ChartParams params,
  ) async {
    try {
      final uri = Uri.parse('${ApiClient.baseUrl}/chart/html/$filename').replace(
        queryParameters: params.toJson().map(
          (key, value) => MapEntry(key, value.toString()),
        ),
      );

      final httpResponse = await http.get(uri, headers: {
        'Content-Type': 'text/html',
        'Accept': 'text/html',
      });

      if (httpResponse.statusCode >= 200 && httpResponse.statusCode < 300) {
        return ApiResponse.success(httpResponse.body);
      } else {
        return ApiResponse.error('HTTP ${httpResponse.statusCode}: ${httpResponse.reasonPhrase}');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // 利用可能なファイル一覧を取得
  static Future<ApiResponse<AvailableFiles>> getAvailableFiles() async {
    return await ApiClient.get<AvailableFiles>(
      '/chart/available-files',
      fromJson: (json) => AvailableFiles.fromJson(json),
    );
  }

  // ファイル情報を取得
  static Future<ApiResponse<ChartFileInfo>> getFileInfo(String filename) async {
    return await ApiClient.get<ChartFileInfo>(
      '/chart/file-info/$filename',
      fromJson: (json) => ChartFileInfo.fromJson(json),
    );
  }
}
