import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'dart:io';
import '../api/chart_api.dart';
import '../models/chart.dart';
import '../utils/constants.dart';

class ChartScreen extends StatefulWidget {
  const ChartScreen({super.key});

  @override
  State<ChartScreen> createState() => _ChartScreenState();
}

class _ChartScreenState extends State<ChartScreen> {
  List<String> _availableFiles = [];
  String? _selectedFile;
  ChartParams _chartParams = ChartParams();
  String? _htmlContent;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadAvailableFiles();
  }

  Future<void> _loadAvailableFiles() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await ChartApi.getAvailableFiles();
      if (response.isSuccess) {
        setState(() {
          _availableFiles = response.data!.files;
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = response.error;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        if (e.toString().contains('HTML instead of JSON')) {
          _errorMessage = 'バックエンドサーバーが起動していません。サーバーを起動してから再試行してください。';
        } else {
          _errorMessage = 'ファイル一覧の取得に失敗しました: $e';
        }
        _isLoading = false;
      });
    }
  }

  Future<void> _loadChart() async {
    if (_selectedFile == null) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // JSONデータを取得
      final response = await ChartApi.getJsonChart(_selectedFile!, _chartParams);
      if (response.isSuccess) {
        setState(() {
          _htmlContent = response.data!['html_content'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = response.error;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'チャートの読み込みに失敗しました: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildControlPanel(),
          Expanded(
            child: _buildChartArea(),
          ),
        ],
      ),
    );
  }

  Widget _buildControlPanel() {
    return Card(
      margin: const EdgeInsets.all(UIConstants.defaultPadding),
      child: Padding(
        padding: const EdgeInsets.all(UIConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'チャート設定',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            
            // ファイル選択
            DropdownButtonFormField<String>(
              value: _selectedFile,
              decoration: const InputDecoration(
                labelText: 'ファイルを選択',
                border: OutlineInputBorder(),
              ),
              items: _availableFiles.map((file) {
                return DropdownMenuItem(
                  value: file,
                  child: Text(file),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedFile = value;
                });
                if (value != null) {
                  _loadChart();
                }
              },
            ),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // テクニカル指標の設定
            Text(
              'テクニカル指標',
              style: TextStyle(
                fontSize: TextStyles.body1Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.smallPadding),
            
            Wrap(
              spacing: UIConstants.smallPadding,
              children: [
                _buildCheckbox('ボリンジャーバンド', _chartParams.showBb, (value) {
                  if (value != null) {
                    setState(() {
                      _chartParams = ChartParams(
                        showBb: value,
                        bbWindow: _chartParams.bbWindow,
                        bbStd: _chartParams.bbStd,
                        showRsi: _chartParams.showRsi,
                        rsiPeriod: _chartParams.rsiPeriod,
                        showMacd: _chartParams.showMacd,
                        macdFast: _chartParams.macdFast,
                        macdSlow: _chartParams.macdSlow,
                        macdSignal: _chartParams.macdSignal,
                        showVwap: _chartParams.showVwap,
                        showMdd: _chartParams.showMdd,
                        annotateDates: _chartParams.annotateDates,
                        markMonthStart: _chartParams.markMonthStart,
                        axisTick: _chartParams.axisTick,
                        axisTickFormat: _chartParams.axisTickFormat,
                        axisTickDates: _chartParams.axisTickDates,
                      );
                    });
                    if (_selectedFile != null) _loadChart();
                  }
                }),
                _buildCheckbox('RSI', _chartParams.showRsi, (value) {
                  if (value != null) {
                    setState(() {
                      _chartParams = ChartParams(
                        showBb: _chartParams.showBb,
                        bbWindow: _chartParams.bbWindow,
                        bbStd: _chartParams.bbStd,
                        showRsi: value,
                        rsiPeriod: _chartParams.rsiPeriod,
                        showMacd: _chartParams.showMacd,
                        macdFast: _chartParams.macdFast,
                        macdSlow: _chartParams.macdSlow,
                        macdSignal: _chartParams.macdSignal,
                        showVwap: _chartParams.showVwap,
                        showMdd: _chartParams.showMdd,
                        annotateDates: _chartParams.annotateDates,
                        markMonthStart: _chartParams.markMonthStart,
                        axisTick: _chartParams.axisTick,
                        axisTickFormat: _chartParams.axisTickFormat,
                        axisTickDates: _chartParams.axisTickDates,
                      );
                    });
                    if (_selectedFile != null) _loadChart();
                  }
                }),
                _buildCheckbox('MACD', _chartParams.showMacd, (value) {
                  if (value != null) {
                    setState(() {
                      _chartParams = ChartParams(
                        showBb: _chartParams.showBb,
                        bbWindow: _chartParams.bbWindow,
                        bbStd: _chartParams.bbStd,
                        showRsi: _chartParams.showRsi,
                        rsiPeriod: _chartParams.rsiPeriod,
                        showMacd: value,
                        macdFast: _chartParams.macdFast,
                        macdSlow: _chartParams.macdSlow,
                        macdSignal: _chartParams.macdSignal,
                        showVwap: _chartParams.showVwap,
                        showMdd: _chartParams.showMdd,
                        annotateDates: _chartParams.annotateDates,
                        markMonthStart: _chartParams.markMonthStart,
                        axisTick: _chartParams.axisTick,
                        axisTickFormat: _chartParams.axisTickFormat,
                        axisTickDates: _chartParams.axisTickDates,
                      );
                    });
                    if (_selectedFile != null) _loadChart();
                  }
                }),
                _buildCheckbox('VWAP', _chartParams.showVwap, (value) {
                  if (value != null) {
                    setState(() {
                      _chartParams = ChartParams(
                        showBb: _chartParams.showBb,
                        bbWindow: _chartParams.bbWindow,
                        bbStd: _chartParams.bbStd,
                        showRsi: _chartParams.showRsi,
                        rsiPeriod: _chartParams.rsiPeriod,
                        showMacd: _chartParams.showMacd,
                        macdFast: _chartParams.macdFast,
                        macdSlow: _chartParams.macdSlow,
                        macdSignal: _chartParams.macdSignal,
                        showVwap: value,
                        showMdd: _chartParams.showMdd,
                        annotateDates: _chartParams.annotateDates,
                        markMonthStart: _chartParams.markMonthStart,
                        axisTick: _chartParams.axisTick,
                        axisTickFormat: _chartParams.axisTickFormat,
                        axisTickDates: _chartParams.axisTickDates,
                      );
                    });
                    if (_selectedFile != null) _loadChart();
                  }
                }),
                _buildCheckbox('最大ドローダウン', _chartParams.showMdd, (value) {
                  if (value != null) {
                    setState(() {
                      _chartParams = ChartParams(
                        showBb: _chartParams.showBb,
                        bbWindow: _chartParams.bbWindow,
                        bbStd: _chartParams.bbStd,
                        showRsi: _chartParams.showRsi,
                        rsiPeriod: _chartParams.rsiPeriod,
                        showMacd: _chartParams.showMacd,
                        macdFast: _chartParams.macdFast,
                        macdSlow: _chartParams.macdSlow,
                        macdSignal: _chartParams.macdSignal,
                        showVwap: _chartParams.showVwap,
                        showMdd: value,
                        annotateDates: _chartParams.annotateDates,
                        markMonthStart: _chartParams.markMonthStart,
                        axisTick: _chartParams.axisTick,
                        axisTickFormat: _chartParams.axisTickFormat,
                        axisTickDates: _chartParams.axisTickDates,
                      );
                    });
                    if (_selectedFile != null) _loadChart();
                  }
                }),
              ],
            ),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // 日付注釈の設定
            Text(
              '日付注釈',
              style: TextStyle(
                fontSize: TextStyles.body1Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.smallPadding),
            
            Wrap(
              spacing: UIConstants.smallPadding,
              children: [
                _buildCheckbox('日付注釈', _chartParams.annotateDates, (value) {
                  if (value != null) {
                    setState(() {
                      _chartParams = ChartParams(
                        showBb: _chartParams.showBb,
                        bbWindow: _chartParams.bbWindow,
                        bbStd: _chartParams.bbStd,
                        showRsi: _chartParams.showRsi,
                        rsiPeriod: _chartParams.rsiPeriod,
                        showMacd: _chartParams.showMacd,
                        macdFast: _chartParams.macdFast,
                        macdSlow: _chartParams.macdSlow,
                        macdSignal: _chartParams.macdSignal,
                        showVwap: _chartParams.showVwap,
                        showMdd: _chartParams.showMdd,
                        annotateDates: value,
                        markMonthStart: _chartParams.markMonthStart,
                        axisTick: _chartParams.axisTick,
                        axisTickFormat: _chartParams.axisTickFormat,
                        axisTickDates: _chartParams.axisTickDates,
                      );
                    });
                    if (_selectedFile != null) _loadChart();
                  }
                }),
                _buildCheckbox('月初マーク', _chartParams.markMonthStart, (value) {
                  if (value != null) {
                    setState(() {
                      _chartParams = ChartParams(
                        showBb: _chartParams.showBb,
                        bbWindow: _chartParams.bbWindow,
                        bbStd: _chartParams.bbStd,
                        showRsi: _chartParams.showRsi,
                        rsiPeriod: _chartParams.rsiPeriod,
                        showMacd: _chartParams.showMacd,
                        macdFast: _chartParams.macdFast,
                        macdSlow: _chartParams.macdSlow,
                        macdSignal: _chartParams.macdSignal,
                        showVwap: _chartParams.showVwap,
                        showMdd: _chartParams.showMdd,
                        annotateDates: _chartParams.annotateDates,
                        markMonthStart: value,
                        axisTick: _chartParams.axisTick,
                        axisTickFormat: _chartParams.axisTickFormat,
                        axisTickDates: _chartParams.axisTickDates,
                      );
                    });
                    if (_selectedFile != null) _loadChart();
                  }
                }),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCheckbox(String label, bool value, ValueChanged<bool?> onChanged) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Checkbox(
          value: value,
          onChanged: onChanged,
          activeColor: Color(AppColors.primaryColor),
        ),
        Text(label),
      ],
    );
  }

  Widget _buildChartArea() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Color(AppColors.errorColor),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            Text(
              'エラーが発生しました',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.errorColor),
              ),
            ),
            const SizedBox(height: UIConstants.smallPadding),
            Text(
              _errorMessage!,
              style: TextStyle(
                fontSize: TextStyles.body1Size,
                color: Color(AppColors.textSecondaryColor),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: UIConstants.largePadding),
            ElevatedButton(
              onPressed: _loadAvailableFiles,
              child: const Text('再試行'),
            ),
          ],
        ),
      );
    }

    if (_selectedFile == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.show_chart,
              size: 64,
              color: Color(AppColors.textSecondaryColor),
            ),
            const SizedBox(height: UIConstants.largePadding),
            Text(
              'ファイルを選択してください',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                color: Color(AppColors.textSecondaryColor),
              ),
            ),
          ],
        ),
      );
    }

    if (_htmlContent == null) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // プラットフォーム固有のチャート表示
    if (kIsWeb) {
      // WebプラットフォームではHTMLを直接表示
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey.shade300),
          borderRadius: BorderRadius.circular(UIConstants.borderRadius),
        ),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'チャート表示（Web版）',
                style: TextStyle(
                  fontSize: TextStyles.headline3Size,
                  fontWeight: FontWeight.bold,
                  color: Color(AppColors.textColor),
                ),
              ),
              const SizedBox(height: UIConstants.defaultPadding),
              Text(
                'Webプラットフォームでは、インタラクティブチャートの表示が制限されています。',
                style: TextStyle(
                  fontSize: TextStyles.body1Size,
                  color: Color(AppColors.textSecondaryColor),
                ),
              ),
              const SizedBox(height: UIConstants.defaultPadding),
              ElevatedButton(
                onPressed: () {
                  // HTMLコンテンツを新しいウィンドウで開く
                  if (kIsWeb && _htmlContent != null) {
                    // dart:htmlを使用して新しいウィンドウを開く
                    // 注意: これはWebプラットフォームでのみ動作
                  }
                },
                child: const Text('新しいウィンドウでチャートを開く'),
              ),
            ],
          ),
        ),
      );
    } else if (Platform.isAndroid || Platform.isIOS) {
      // モバイルプラットフォームではWebViewを使用
      // 注意: WebViewはモバイル専用
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey.shade300),
          borderRadius: BorderRadius.circular(UIConstants.borderRadius),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.show_chart,
                size: 64,
                color: Color(AppColors.textSecondaryColor),
              ),
              const SizedBox(height: UIConstants.largePadding),
              Text(
                'モバイルプラットフォーム',
                style: TextStyle(
                  fontSize: TextStyles.headline3Size,
                  fontWeight: FontWeight.bold,
                  color: Color(AppColors.textColor),
                ),
              ),
              const SizedBox(height: UIConstants.defaultPadding),
              Text(
                'モバイルプラットフォームでは、WebViewを使用してチャートを表示します。',
                style: TextStyle(
                  fontSize: TextStyles.body1Size,
                  color: Color(AppColors.textSecondaryColor),
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    } else {
      // その他のプラットフォームではHTMLをテキストとして表示
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey.shade300),
          borderRadius: BorderRadius.circular(UIConstants.borderRadius),
        ),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'チャート表示（デスクトップ版）',
                style: TextStyle(
                  fontSize: TextStyles.headline3Size,
                  fontWeight: FontWeight.bold,
                  color: Color(AppColors.textColor),
                ),
              ),
              const SizedBox(height: UIConstants.defaultPadding),
              Text(
                'デスクトッププラットフォームでは、インタラクティブチャートの表示が制限されています。',
                style: TextStyle(
                  fontSize: TextStyles.body1Size,
                  color: Color(AppColors.textSecondaryColor),
                ),
              ),
              const SizedBox(height: UIConstants.defaultPadding),
              Text(
                'HTMLコンテンツ:',
                style: TextStyle(
                  fontSize: TextStyles.body1Size,
                  fontWeight: FontWeight.bold,
                  color: Color(AppColors.textColor),
                ),
              ),
              const SizedBox(height: UIConstants.smallPadding),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  _htmlContent!,
                  style: TextStyle(
                    fontSize: TextStyles.body2Size,
                    fontFamily: 'monospace',
                    color: Color(AppColors.textColor),
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }
  }
}
