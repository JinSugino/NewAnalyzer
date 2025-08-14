// 分析関連のモデル定義

// 分析パラメータ
class AnalysisParams {
  final List<String>? tickers;
  final double riskFreeRate;
  final int periodsPerYear;
  final String method; // "simple" or "log"

  AnalysisParams({
    this.tickers,
    this.riskFreeRate = 0.0,
    this.periodsPerYear = 252,
    this.method = 'simple',
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'risk_free_rate': riskFreeRate,
      'periods_per_year': periodsPerYear,
      'method': method,
    };
    
    if (tickers != null) {
      data['tickers'] = tickers;
    }
    
    return data;
  }
}

// 統計サマリー
class StatisticalSummary {
  final String symbol;
  final double meanReturn;
  final double volatility;
  final double sharpeRatio;
  final double maxDrawdown;
  final double totalReturn;

  StatisticalSummary({
    required this.symbol,
    required this.meanReturn,
    required this.volatility,
    required this.sharpeRatio,
    required this.maxDrawdown,
    required this.totalReturn,
  });

  factory StatisticalSummary.fromJson(Map<String, dynamic> json) {
    return StatisticalSummary(
      symbol: json['symbol'] ?? '',
      meanReturn: (json['mean_return'] ?? 0.0).toDouble(),
      volatility: (json['volatility'] ?? 0.0).toDouble(),
      sharpeRatio: (json['sharpe_ratio'] ?? 0.0).toDouble(),
      maxDrawdown: (json['max_drawdown'] ?? 0.0).toDouble(),
      totalReturn: (json['total_return'] ?? 0.0).toDouble(),
    );
  }
}

// 相関行列
class CorrelationMatrix {
  final Map<String, Map<String, double>> correlations;
  final List<String> symbols;

  CorrelationMatrix({
    required this.correlations,
    required this.symbols,
  });

  factory CorrelationMatrix.fromJson(Map<String, dynamic> json) {
    final correlationsData = Map<String, dynamic>.from(json['correlations'] ?? {});
    final correlations = <String, Map<String, double>>{};
    
    correlationsData.forEach((key, value) {
      if (value is Map) {
        correlations[key] = Map<String, double>.from(value);
      }
    });

    return CorrelationMatrix(
      correlations: correlations,
      symbols: List<String>.from(json['symbols'] ?? []),
    );
  }

  double? getCorrelation(String symbol1, String symbol2) {
    return correlations[symbol1]?[symbol2];
  }
}

// 統合相関分析結果
class ConsolidatedCorrelationResult {
  final CorrelationMatrix originalCorrelation;
  final CorrelationMatrix consolidatedCorrelation;
  final List<List<String>> groups;
  final Map<String, dynamic> consolidationInfo;

  ConsolidatedCorrelationResult({
    required this.originalCorrelation,
    required this.consolidatedCorrelation,
    required this.groups,
    required this.consolidationInfo,
  });

  factory ConsolidatedCorrelationResult.fromJson(Map<String, dynamic> json) {
    return ConsolidatedCorrelationResult(
      originalCorrelation: CorrelationMatrix.fromJson(json['original_correlation'] ?? {}),
      consolidatedCorrelation: CorrelationMatrix.fromJson(json['consolidated_correlation'] ?? {}),
      groups: (json['groups'] as List?)
          ?.map((group) => List<String>.from(group))
          .toList() ?? [],
      consolidationInfo: Map<String, dynamic>.from(json['consolidation_info'] ?? {}),
    );
  }
}

// 分析結果サマリー
class AnalysisSummary {
  final List<StatisticalSummary> summaries;
  final int count;

  AnalysisSummary({
    required this.summaries,
    required this.count,
  });

  factory AnalysisSummary.fromJson(Map<String, dynamic> json) {
    return AnalysisSummary(
      summaries: (json['summaries'] as List?)
          ?.map((item) => StatisticalSummary.fromJson(item))
          .toList() ?? [],
      count: json['count'] ?? 0,
    );
  }
}

// 相関分析パラメータ
class CorrelationParams {
  final List<String>? tickers;
  final String method;
  final double correlationThreshold;
  final String consolidationMethod;

  CorrelationParams({
    this.tickers,
    this.method = 'simple',
    this.correlationThreshold = 0.9,
    this.consolidationMethod = 'mean',
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'method': method,
      'correlation_threshold': correlationThreshold,
      'consolidation_method': consolidationMethod,
    };
    
    if (tickers != null) {
      data['tickers'] = tickers;
    }
    
    return data;
  }
}
