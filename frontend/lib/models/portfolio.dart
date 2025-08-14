// ポートフォリオ関連のモデル定義

// ポートフォリオパラメータ
class PortfolioParams {
  final List<String>? tickers;
  final String method;
  final bool annualize;
  final int periodsPerYear;
  final double riskFreeRate;
  final bool allowShort;
  final double? targetReturnMin;
  final double? targetReturnMax;
  final int numFrontierPoints;
  final int numSamples;
  final double maxLeverage;
  final bool consolidateCorrelated;
  final double correlationThreshold;
  final String consolidationMethod;
  final String optimizationMethod;
  final double? targetReturn;
  final double? targetRisk;
  final double riskTolerance;
  final double maxWeight;
  final double minWeight;

  PortfolioParams({
    this.tickers,
    this.method = 'simple',
    this.annualize = true,
    this.periodsPerYear = 252,
    this.riskFreeRate = 0.0,
    this.allowShort = true,
    this.targetReturnMin,
    this.targetReturnMax,
    this.numFrontierPoints = 50,
    this.numSamples = 2000,
    this.maxLeverage = 2.0,
    this.consolidateCorrelated = false,
    this.correlationThreshold = 0.9,
    this.consolidationMethod = 'mean',
    this.optimizationMethod = 'sharpe',
    this.targetReturn,
    this.targetRisk,
    this.riskTolerance = 1.0,
    this.maxWeight = 1.0,
    this.minWeight = 0.0,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'method': method,
      'annualize': annualize,
      'periods_per_year': periodsPerYear,
      'r_f': riskFreeRate,
      'allow_short': allowShort,
      'num_frontier_points': numFrontierPoints,
      'num_samples': numSamples,
      'max_leverage': maxLeverage,
      'consolidate_correlated': consolidateCorrelated,
      'correlation_threshold': correlationThreshold,
      'consolidation_method': consolidationMethod,
      'optimization_method': optimizationMethod,
      'risk_tolerance': riskTolerance,
      'max_weight': maxWeight,
      'min_weight': minWeight,
    };
    
    if (tickers != null) {
      data['tickers'] = tickers;
    }
    if (targetReturnMin != null) {
      data['target_return_min'] = targetReturnMin;
    }
    if (targetReturnMax != null) {
      data['target_return_max'] = targetReturnMax;
    }
    if (targetReturn != null) {
      data['target_return'] = targetReturn;
    }
    if (targetRisk != null) {
      data['target_risk'] = targetRisk;
    }
    
    return data;
  }
}

// ポートフォリオ入力データ
class PortfolioInputs {
  final List<String> symbols;
  final List<double> expectedReturns;
  final Map<String, Map<String, double>> covarianceMatrix;
  final double riskFreeRate;

  PortfolioInputs({
    required this.symbols,
    required this.expectedReturns,
    required this.covarianceMatrix,
    required this.riskFreeRate,
  });

  factory PortfolioInputs.fromJson(Map<String, dynamic> json) {
    final covarianceData = Map<String, dynamic>.from(json['covariance_matrix'] ?? {});
    final covarianceMatrix = <String, Map<String, double>>{};
    
    covarianceData.forEach((key, value) {
      if (value is Map) {
        covarianceMatrix[key] = Map<String, double>.from(value);
      }
    });

    return PortfolioInputs(
      symbols: List<String>.from(json['symbols'] ?? []),
      expectedReturns: List<double>.from(json['expected_returns'] ?? []),
      covarianceMatrix: covarianceMatrix,
      riskFreeRate: (json['risk_free_rate'] ?? 0.0).toDouble(),
    );
  }
}

// 効率的フロンティアポイント
class EfficientFrontierPoint {
  final double risk;
  final double return_;
  final List<double> weights;

  EfficientFrontierPoint({
    required this.risk,
    required this.return_,
    required this.weights,
  });

  factory EfficientFrontierPoint.fromJson(Map<String, dynamic> json) {
    return EfficientFrontierPoint(
      risk: (json['risk'] ?? 0.0).toDouble(),
      return_: (json['return'] ?? 0.0).toDouble(),
      weights: List<double>.from(json['weights'] ?? []),
    );
  }
}

// ポートフォリオウェイト
class PortfolioWeights {
  final String symbol;
  final double weight;
  final bool isShort;

  PortfolioWeights({
    required this.symbol,
    required this.weight,
    required this.isShort,
  });

  factory PortfolioWeights.fromJson(Map<String, dynamic> json) {
    return PortfolioWeights(
      symbol: json['symbol'] ?? '',
      weight: (json['weight'] ?? 0.0).toDouble(),
      isShort: json['is_short'] ?? false,
    );
  }
}

// 特殊ポートフォリオ
class SpecialPortfolio {
  final String type; // "tangency", "minimum_variance", etc.
  final double risk;
  final double return_;
  final List<PortfolioWeights> weights;

  SpecialPortfolio({
    required this.type,
    required this.risk,
    required this.return_,
    required this.weights,
  });

  factory SpecialPortfolio.fromJson(Map<String, dynamic> json) {
    return SpecialPortfolio(
      type: json['type'] ?? '',
      risk: (json['risk'] ?? 0.0).toDouble(),
      return_: (json['return'] ?? 0.0).toDouble(),
      weights: (json['weights'] as List?)
          ?.map((item) => PortfolioWeights.fromJson(item))
          .toList() ?? [],
    );
  }
}

// ポートフォリオ結果
class PortfolioResult {
  final PortfolioInputs inputs;
  final List<EfficientFrontierPoint> efficientFrontier;
  final List<Map<String, dynamic>> feasibleSet;
  final SpecialPortfolio? tangencyPortfolio;
  final SpecialPortfolio? minimumVariancePortfolio;
  final String? htmlContent;

  PortfolioResult({
    required this.inputs,
    required this.efficientFrontier,
    required this.feasibleSet,
    this.tangencyPortfolio,
    this.minimumVariancePortfolio,
    this.htmlContent,
  });

  factory PortfolioResult.fromJson(Map<String, dynamic> json) {
    return PortfolioResult(
      inputs: PortfolioInputs.fromJson(json['inputs'] ?? {}),
      efficientFrontier: (json['efficient_frontier'] as List?)
          ?.map((item) => EfficientFrontierPoint.fromJson(item))
          .toList() ?? [],
      feasibleSet: (json['feasible_set'] as List?)
          ?.map((item) => Map<String, dynamic>.from(item))
          .toList() ?? [],
      tangencyPortfolio: json['tangency_portfolio'] != null
          ? SpecialPortfolio.fromJson(json['tangency_portfolio'])
          : null,
      minimumVariancePortfolio: json['minimum_variance_portfolio'] != null
          ? SpecialPortfolio.fromJson(json['minimum_variance_portfolio'])
          : null,
      htmlContent: json['html_content'],
    );
  }
}
