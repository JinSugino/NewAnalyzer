import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'dart:io';
import 'package:webview_flutter/webview_flutter.dart';
import '../api/chart_api.dart';
import '../models/chart.dart';
import '../utils/constants.dart';

// Webプラットフォーム用のdart:html
import 'dart:html' as html if (dart.library.io) 'dart:io' as html;

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
  WebViewController? _webViewController;
  html.Element? _webElement;

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
      // HTMLコンテンツを直接取得
      final response = await ChartApi.getHtmlChart(_selectedFile!, _chartParams);
      if (response.isSuccess) {
        setState(() {
          _htmlContent = response.data!;
          _isLoading = false;
        });
        
        // WebViewにHTMLを読み込み
        if (_webViewController != null && _htmlContent != null) {
          await _webViewController!.loadHtmlString(_htmlContent!);
        }
        
        // Webプラットフォーム用のiframe更新
        if (kIsWeb && _htmlContent != null) {
          _updateWebIframe();
        }
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

  void _updateWebIframe() {
    if (kIsWeb && _htmlContent != null) {
      // 既存のiframeを削除
      if (_webElement != null) {
        _webElement!.remove();
      }
      
      // 新しいiframeを作成
      final iframe = html.IFrameElement()
        ..src = 'data:text/html;charset=utf-8,${Uri.encodeComponent(_htmlContent!)}'
        ..style.border = 'none'
        ..style.width = '100%'
        ..style.height = '100%'
        ..allowFullscreen = true;
      
      _webElement = iframe;
      
      // DOMに追加
      html.document.body?.append(iframe);
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

    // チャート表示エリア
    return Container(
      width: double.infinity,
      height: double.infinity,
      child: _htmlContent != null
          ? _buildChartWidget()
          : Center(
              child: Text(
                'チャートを読み込み中...',
                style: TextStyle(
                  fontSize: TextStyles.body1Size,
                  color: Color(AppColors.textSecondaryColor),
                ),
              ),
            ),
    );
  }

  Widget _buildChartWidget() {
    if (kIsWeb) {
      // WebプラットフォームではHtmlElementViewを使用
      return HtmlElementView(
        viewType: 'chart-iframe',
        onPlatformViewCreated: (int id) {
          // iframeの作成
          _createWebIframe();
        },
      );
    } else {
      // モバイル・デスクトッププラットフォームではWebViewを使用
      return WebViewWidget(
        controller: _webViewController ?? _createWebViewController(),
      );
    }
  }

  void _createWebIframe() {
    if (kIsWeb && _htmlContent != null) {
      // 既存のiframeを削除
      if (_webElement != null) {
        _webElement!.remove();
      }
      
      // 新しいiframeを作成
      final iframe = html.IFrameElement()
        ..src = 'data:text/html;charset=utf-8,${Uri.encodeComponent(_htmlContent!)}'
        ..style.border = 'none'
        ..style.width = '100%'
        ..style.height = '100%'
        ..allowFullscreen = true;
      
      _webElement = iframe;
      
      // DOMに追加
      html.document.body?.append(iframe);
    }
  }

  WebViewController _createWebViewController() {
    final controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(Colors.white)
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {
            // 読み込み進捗
          },
          onPageStarted: (String url) {
            // ページ読み込み開始
          },
          onPageFinished: (String url) {
            // ページ読み込み完了
          },
          onWebResourceError: (WebResourceError error) {
            // エラー処理
            setState(() {
              _errorMessage = 'WebViewエラー: ${error.description}';
            });
          },
        ),
      );

    _webViewController = controller;
    
    // HTMLコンテンツが既にある場合は読み込み
    if (_htmlContent != null) {
      controller.loadHtmlString(_htmlContent!);
    }

    return controller;
  }
}
