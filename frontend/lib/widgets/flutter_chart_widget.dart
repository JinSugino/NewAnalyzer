import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_charts/charts.dart';
import '../models/chart_data.dart';
import '../utils/constants.dart';

class FlutterChartWidget extends StatelessWidget {
  final ChartData chartData;

  const FlutterChartWidget({
    super.key,
    required this.chartData,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(UIConstants.defaultPadding),
      child: Padding(
        padding: const EdgeInsets.all(UIConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              chartData.ticker,
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            SizedBox(
              height: 400,
              child: _buildChart(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChart() {
    // メインのローソク足チャートを探す
    final candlestickTrace = chartData.data.data.firstWhere(
      (trace) => trace.type == 'candlestick',
      orElse: () => chartData.data.data.first,
    );

    if (candlestickTrace.type == 'candlestick') {
      return _buildCandlestickChart(candlestickTrace);
    } else {
      return _buildLineChart(candlestickTrace);
    }
  }

  Widget _buildCandlestickChart(PlotlyTrace trace) {
    final candlestickData = _convertToCandlestickData(trace);
    
    return SfCartesianChart(
      primaryXAxis: DateTimeAxis(),
      primaryYAxis: NumericAxis(),
      series: <CartesianSeries>[
        CandleSeries<CandlestickData, DateTime>(
          dataSource: candlestickData,
          xValueMapper: (CandlestickData data, _) => data.time,
          lowValueMapper: (CandlestickData data, _) => data.low,
          highValueMapper: (CandlestickData data, _) => data.high,
          openValueMapper: (CandlestickData data, _) => data.open,
          closeValueMapper: (CandlestickData data, _) => data.close,
          name: 'Price',
        ),
        ..._buildIndicatorSeries(),
      ],
    );
  }

  Widget _buildLineChart(PlotlyTrace trace) {
    final lineData = _convertToLineData(trace);
    
    return SfCartesianChart(
      primaryXAxis: DateTimeAxis(),
      primaryYAxis: NumericAxis(),
      series: <CartesianSeries>[
        LineSeries<LineData, DateTime>(
          dataSource: lineData,
          xValueMapper: (LineData data, _) => data.time,
          yValueMapper: (LineData data, _) => data.value,
          name: trace.name ?? 'Data',
        ),
        ..._buildIndicatorSeries(),
      ],
    );
  }

  List<CartesianSeries> _buildIndicatorSeries() {
    final List<CartesianSeries> series = [];
    
    for (final trace in chartData.data.data) {
      if (trace.type == 'scatter' && trace.name != null) {
        final lineData = _convertToLineData(trace);
        if (lineData.isNotEmpty) {
          series.add(
            LineSeries<LineData, DateTime>(
              dataSource: lineData,
              xValueMapper: (LineData data, _) => data.time,
              yValueMapper: (LineData data, _) => data.value,
              name: trace.name!,
              color: _getColorForIndicator(trace.name!),
            ),
          );
        }
      }
    }
    
    return series;
  }

  List<CandlestickData> _convertToCandlestickData(PlotlyTrace trace) {
    final List<CandlestickData> result = [];
    
    for (int i = 0; i < trace.x.length; i++) {
      final x = trace.x[i];
      final y = trace.y[i];
      
      if (y is Map<String, dynamic>) {
        result.add(
          CandlestickData(
            time: DateTime.parse(x.toString()),
            open: (y['open'] as num).toDouble(),
            high: (y['high'] as num).toDouble(),
            low: (y['low'] as num).toDouble(),
            close: (y['close'] as num).toDouble(),
          ),
        );
      }
    }
    
    return result;
  }

  List<LineData> _convertToLineData(PlotlyTrace trace) {
    final List<LineData> result = [];
    
    for (int i = 0; i < trace.x.length; i++) {
      final x = trace.x[i];
      final y = trace.y[i];
      
      if (x != null && y != null) {
        result.add(
          LineData(
            time: DateTime.parse(x.toString()),
            value: (y as num).toDouble(),
          ),
        );
      }
    }
    
    return result;
  }

  Color _getColorForIndicator(String name) {
    switch (name.toLowerCase()) {
      case 'bb_upper':
        return Colors.blue;
      case 'bb_lower':
        return Colors.blue;
      case 'bb_middle':
        return Colors.orange;
      case 'rsi':
        return Colors.purple;
      case 'macd':
        return Colors.green;
      case 'vwap':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

class CandlestickData {
  final DateTime time;
  final double open;
  final double high;
  final double low;
  final double close;

  CandlestickData({
    required this.time,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
  });
}

class LineData {
  final DateTime time;
  final double value;

  LineData({
    required this.time,
    required this.value,
  });
}
