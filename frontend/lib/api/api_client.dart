import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  static const String baseUrl = 'http://127.0.0.1:8000';
  
  // 共通ヘッダー
  static Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // GET リクエスト
  static Future<ApiResponse<T>> get<T>(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint').replace(
        queryParameters: queryParameters?.map(
          (key, value) => MapEntry(key, value.toString()),
        ),
      );

      final response = await http.get(uri, headers: _headers);
      
      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // POST リクエスト
  static Future<ApiResponse<T>> post<T>(
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint').replace(
        queryParameters: queryParameters?.map(
          (key, value) => MapEntry(key, value.toString()),
        ),
      );

      final response = await http.post(
        uri,
        headers: _headers,
        body: body != null ? jsonEncode(body) : null,
      );
      
      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // DELETE リクエスト
  static Future<ApiResponse<T>> delete<T>(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    T Function(Map<String, dynamic>)? fromJson,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint').replace(
        queryParameters: queryParameters?.map(
          (key, value) => MapEntry(key, value.toString()),
        ),
      );

      final response = await http.delete(uri, headers: _headers);
      
      return _handleResponse<T>(response, fromJson);
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // レスポンス処理
  static ApiResponse<T> _handleResponse<T>(
    http.Response response,
    T Function(Map<String, dynamic>)? fromJson,
  ) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      try {
        if (response.body.isEmpty) {
          return ApiResponse.success(null as T);
        }
        
        // HTMLレスポンスの場合はエラーとして扱う
        if (response.body.trim().toLowerCase().startsWith('<!doctype') ||
            response.body.trim().toLowerCase().startsWith('<html')) {
          return ApiResponse.error('Server returned HTML instead of JSON. Status: ${response.statusCode}');
        }
        
        final jsonData = jsonDecode(response.body);
        
        if (fromJson != null) {
          final data = fromJson(jsonData);
          return ApiResponse.success(data);
        } else {
          return ApiResponse.success(jsonData as T);
        }
      } catch (e) {
        return ApiResponse.error('JSON parsing error: $e');
      }
    } else {
      try {
        // HTMLエラーページの場合は適切なエラーメッセージを返す
        if (response.body.trim().toLowerCase().startsWith('<!doctype') ||
            response.body.trim().toLowerCase().startsWith('<html')) {
          return ApiResponse.error('Server error (${response.statusCode}): ${response.reasonPhrase}');
        }
        
        final errorData = jsonDecode(response.body);
        final errorMessage = errorData['detail'] ?? 'HTTP ${response.statusCode}';
        return ApiResponse.error(errorMessage);
      } catch (e) {
        return ApiResponse.error('HTTP ${response.statusCode}: ${response.reasonPhrase}');
      }
    }
  }

  // ヘルスチェック
  static Future<bool> isServerAvailable() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: _headers,
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

// APIレスポンスのラッパークラス
class ApiResponse<T> {
  final T? data;
  final String? error;
  final bool isSuccess;

  ApiResponse._({
    this.data,
    this.error,
    required this.isSuccess,
  });

  factory ApiResponse.success(T data) {
    return ApiResponse._(data: data, isSuccess: true);
  }

  factory ApiResponse.error(String error) {
    return ApiResponse._(error: error, isSuccess: false);
  }

  // 成功時のデータを取得（nullの場合は例外を投げる）
  T get requireData {
    if (!isSuccess || data == null) {
      throw Exception(error ?? 'No data available');
    }
    return data!;
  }
}
