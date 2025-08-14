import 'package:http/http.dart' as http;
import '../models/analysis.dart';
import 'api_client.dart';

class AnalysisApi {
  // 統計サマリーを取得
  static Future<ApiResponse<AnalysisSummary>> getSummary(
    AnalysisParams params,
  ) async {
    return await ApiClient.get<AnalysisSummary>(
      '/analysis/summary',
      queryParameters: params.toJson(),
      fromJson: (json) => AnalysisSummary.fromJson(json),
    );
  }

  // HTML統計サマリーを取得
  static Future<ApiResponse<String>> getSummaryHtml(
    AnalysisParams params,
  ) async {
    try {
      final uri = Uri.parse('${ApiClient.baseUrl}/analysis/summary/html').replace(
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

  // 相関行列を取得
  static Future<ApiResponse<CorrelationMatrix>> getCorrelation(
    CorrelationParams params,
  ) async {
    return await ApiClient.get<CorrelationMatrix>(
      '/analysis/correlation',
      queryParameters: params.toJson(),
      fromJson: (json) => CorrelationMatrix.fromJson(json),
    );
  }

  // HTML相関ヒートマップを取得
  static Future<ApiResponse<String>> getCorrelationHtml(
    CorrelationParams params,
  ) async {
    try {
      final uri = Uri.parse('${ApiClient.baseUrl}/analysis/correlation/html').replace(
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

  // 統合相関分析を取得
  static Future<ApiResponse<ConsolidatedCorrelationResult>> getConsolidatedCorrelation(
    CorrelationParams params,
  ) async {
    return await ApiClient.get<ConsolidatedCorrelationResult>(
      '/analysis/consolidated-correlation',
      queryParameters: params.toJson(),
      fromJson: (json) => ConsolidatedCorrelationResult.fromJson(json),
    );
  }

  // HTML統合相関ヒートマップを取得
  static Future<ApiResponse<String>> getConsolidatedCorrelationHtml(
    CorrelationParams params,
  ) async {
    try {
      final uri = Uri.parse('${ApiClient.baseUrl}/analysis/consolidated-correlation/html').replace(
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
}
