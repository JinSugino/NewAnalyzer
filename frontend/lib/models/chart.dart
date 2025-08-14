// チャート関連のモデル定義

// チャートパラメータ
class ChartParams {
  final bool showBb;
  final int bbWindow;
  final double bbStd;
  final bool showRsi;
  final int rsiPeriod;
  final bool showMacd;
  final int macdFast;
  final int macdSlow;
  final int macdSignal;
  final bool showVwap;
  final bool showMdd;
  final bool annotateDates;
  final bool markMonthStart;
  final int axisTick;
  final String axisTickFormat;
  final List<String>? axisTickDates;

  ChartParams({
    this.showBb = false,
    this.bbWindow = 20,
    this.bbStd = 2.0,
    this.showRsi = false,
    this.rsiPeriod = 14,
    this.showMacd = false,
    this.macdFast = 12,
    this.macdSlow = 26,
    this.macdSignal = 9,
    this.showVwap = false,
    this.showMdd = false,
    this.annotateDates = false,
    this.markMonthStart = false,
    this.axisTick = 10,
    this.axisTickFormat = '%Y-%m-%d',
    this.axisTickDates,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'show_bb': showBb,
      'bb_window': bbWindow,
      'bb_std': bbStd,
      'show_rsi': showRsi,
      'rsi_period': rsiPeriod,
      'show_macd': showMacd,
      'macd_fast': macdFast,
      'macd_slow': macdSlow,
      'macd_signal': macdSignal,
      'show_vwap': showVwap,
      'show_mdd': showMdd,
      'annotate_dates': annotateDates,
      'mark_month_start': markMonthStart,
      'axis_tick': axisTick,
      'axis_tick_format': axisTickFormat,
    };
    
    if (axisTickDates != null) {
      data['axis_tick_dates'] = axisTickDates;
    }
    
    return data;
  }
}

// 株価データ
class StockData {
  final String date;
  final double open;
  final double high;
  final double low;
  final double close;
  final int volume;

  StockData({
    required this.date,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.volume,
  });

  factory StockData.fromJson(Map<String, dynamic> json) {
    return StockData(
      date: json['Date'] ?? '',
      open: (json['Open'] ?? 0.0).toDouble(),
      high: (json['High'] ?? 0.0).toDouble(),
      low: (json['Low'] ?? 0.0).toDouble(),
      close: (json['Close'] ?? 0.0).toDouble(),
      volume: json['Volume'] ?? 0,
    );
  }
}

// チャートデータ（レガシー）
class ChartDataLegacy {
  final List<StockData> data;
  final Map<String, dynamic> metadata;
  final String? htmlContent;

  ChartDataLegacy({
    required this.data,
    required this.metadata,
    this.htmlContent,
  });

  factory ChartDataLegacy.fromJson(Map<String, dynamic> json) {
    return ChartDataLegacy(
      data: (json['data'] as List?)
          ?.map((item) => StockData.fromJson(item))
          .toList() ?? [],
      metadata: Map<String, dynamic>.from(json['metadata'] ?? {}),
      htmlContent: json['html_content'],
    );
  }
}

// ファイル情報
class ChartFileInfo {
  final String filename;
  final String symbol;
  final String companyName;
  final String sector;
  final String industry;
  final String currency;
  final String exchange;
  final int dataPoints;
  final String startDate;
  final String endDate;
  final String provider;

  ChartFileInfo({
    required this.filename,
    required this.symbol,
    required this.companyName,
    required this.sector,
    required this.industry,
    required this.currency,
    required this.exchange,
    required this.dataPoints,
    required this.startDate,
    required this.endDate,
    required this.provider,
  });

  factory ChartFileInfo.fromJson(Map<String, dynamic> json) {
    return ChartFileInfo(
      filename: json['filename'] ?? '',
      symbol: json['symbol'] ?? '',
      companyName: json['company_name'] ?? '',
      sector: json['sector'] ?? '',
      industry: json['industry'] ?? '',
      currency: json['currency'] ?? '',
      exchange: json['exchange'] ?? '',
      dataPoints: json['data_points'] ?? 0,
      startDate: json['start_date'] ?? '',
      endDate: json['end_date'] ?? '',
      provider: json['provider'] ?? '',
    );
  }
}

// 利用可能ファイル一覧
class AvailableFiles {
  final List<String> files;
  final int count;

  AvailableFiles({
    required this.files,
    required this.count,
  });

  factory AvailableFiles.fromJson(Map<String, dynamic> json) {
    return AvailableFiles(
      files: List<String>.from(json['files'] ?? []),
      count: json['count'] ?? 0,
    );
  }
}
