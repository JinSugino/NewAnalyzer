import 'package:http/http.dart' as http;
import '../models/portfolio.dart';
import 'api_client.dart';

class PortfolioApi {
  // ポートフォリオ入力データを取得
  static Future<ApiResponse<PortfolioInputs>> getInputs(
    PortfolioParams params,
  ) async {
    return await ApiClient.get<PortfolioInputs>(
      '/portfolio/inputs',
      queryParameters: params.toJson(),
      fromJson: (json) => PortfolioInputs.fromJson(json),
    );
  }

  // 実行可能ポートフォリオ集合を取得
  static Future<ApiResponse<PortfolioResult>> getFeasibleSet(
    PortfolioParams params,
  ) async {
    return await ApiClient.get<PortfolioResult>(
      '/portfolio/feasible',
      queryParameters: params.toJson(),
      fromJson: (json) => PortfolioResult.fromJson(json),
    );
  }

  // HTMLポートフォリオ集合を取得
  static Future<ApiResponse<String>> getFeasibleSetHtml(
    PortfolioParams params,
  ) async {
    final response = await ApiClient.get<Map<String, dynamic>>(
      '/portfolio/feasible/html',
      queryParameters: params.toJson(),
    );

    if (response.isSuccess && response.data != null) {
      return ApiResponse.success(response.data!['html_content'] ?? '');
    } else {
      return ApiResponse.error(response.error ?? 'Failed to get portfolio HTML');
    }
  }

  // ポートフォリオ最適化HTMLを取得
  static Future<ApiResponse<String>> getOptimizationHtml(
    PortfolioParams params,
  ) async {
    try {
      final uri = Uri.parse('${ApiClient.baseUrl}/portfolio/optimization/html').replace(
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

  // 効率的フロンティアHTMLを取得
  static Future<ApiResponse<String>> getEfficientFrontierHtml(
    PortfolioParams params,
  ) async {
    try {
      final uri = Uri.parse('${ApiClient.baseUrl}/portfolio/efficient-frontier/html').replace(
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
