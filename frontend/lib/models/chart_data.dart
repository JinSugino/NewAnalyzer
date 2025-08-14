class ChartData {
  final bool success;
  final PlotlyData data;
  final String ticker;
  final String htmlContent;

  ChartData({
    required this.success,
    required this.data,
    required this.ticker,
    required this.htmlContent,
  });

  factory ChartData.fromJson(Map<String, dynamic> json) {
    return ChartData(
      success: json['success'] ?? false,
      data: PlotlyData.fromJson(json['data'] ?? {}),
      ticker: json['ticker'] ?? '',
      htmlContent: json['html_content'] ?? '',
    );
  }
}

class PlotlyData {
  final List<PlotlyTrace> data;
  final PlotlyLayout layout;

  PlotlyData({
    required this.data,
    required this.layout,
  });

  factory PlotlyData.fromJson(Map<String, dynamic> json) {
    return PlotlyData(
      data: (json['data'] as List<dynamic>?)
          ?.map((trace) => PlotlyTrace.fromJson(trace))
          .toList() ?? [],
      layout: PlotlyLayout.fromJson(json['layout'] ?? {}),
    );
  }
}

class PlotlyTrace {
  final List<dynamic> x;
  final List<dynamic> y;
  final String? type;
  final String? name;
  final Map<String, dynamic>? line;
  final Map<String, dynamic>? marker;

  PlotlyTrace({
    required this.x,
    required this.y,
    this.type,
    this.name,
    this.line,
    this.marker,
  });

  factory PlotlyTrace.fromJson(Map<String, dynamic> json) {
    return PlotlyTrace(
      x: json['x'] ?? [],
      y: json['y'] ?? [],
      type: json['type'],
      name: json['name'],
      line: json['line'],
      marker: json['marker'],
    );
  }
}

class PlotlyLayout {
  final String? title;
  final Map<String, dynamic>? xaxis;
  final Map<String, dynamic>? yaxis;
  final Map<String, dynamic>? yaxis2;
  final Map<String, dynamic>? yaxis3;

  PlotlyLayout({
    this.title,
    this.xaxis,
    this.yaxis,
    this.yaxis2,
    this.yaxis3,
  });

  factory PlotlyLayout.fromJson(Map<String, dynamic> json) {
    return PlotlyLayout(
      title: json['title'],
      xaxis: json['xaxis'],
      yaxis: json['yaxis'],
      yaxis2: json['yaxis2'],
      yaxis3: json['yaxis3'],
    );
  }
}
