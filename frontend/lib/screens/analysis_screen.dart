import 'package:flutter/material.dart';
import '../api/analysis_api.dart';
import '../api/api_client.dart';
import '../models/analysis.dart';
import '../utils/constants.dart';

class AnalysisScreen extends StatefulWidget {
  const AnalysisScreen({super.key});

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  AnalysisParams _analysisParams = AnalysisParams();
  CorrelationParams _correlationParams = CorrelationParams();
  String? _htmlContent;
  bool _isLoading = false;
  String? _errorMessage;
  String _currentView = 'summary'; // 'summary', 'correlation', 'consolidated'

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildControlPanel(),
          Expanded(
            child: _buildAnalysisArea(),
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
              '分析設定',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            
            // 分析タイプの選択
            Row(
              children: [
                Expanded(
                  child: _buildAnalysisTypeButton('統計サマリー', 'summary'),
                ),
                const SizedBox(width: UIConstants.smallPadding),
                Expanded(
                  child: _buildAnalysisTypeButton('相関分析', 'correlation'),
                ),
                const SizedBox(width: UIConstants.smallPadding),
                Expanded(
                  child: _buildAnalysisTypeButton('統合相関', 'consolidated'),
                ),
              ],
            ),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // パラメータ設定
            if (_currentView == 'summary') ...[
              _buildSummaryParams(),
            ] else ...[
              _buildCorrelationParams(),
            ],
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // 実行ボタン
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _runAnalysis,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('分析実行'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalysisTypeButton(String label, String type) {
    final isSelected = _currentView == type;
    return ElevatedButton(
      onPressed: () {
        setState(() {
          _currentView = type;
          _htmlContent = null;
          _errorMessage = null;
        });
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected 
            ? Color(AppColors.primaryColor) 
            : Color(AppColors.surfaceColor),
        foregroundColor: isSelected 
            ? Colors.white 
            : Color(AppColors.textColor),
        side: BorderSide(
          color: Color(AppColors.primaryColor),
          width: 1,
        ),
      ),
      child: Text(label),
    );
  }

  Widget _buildSummaryParams() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '統計サマリーパラメータ',
          style: TextStyle(
            fontSize: TextStyles.body1Size,
            fontWeight: FontWeight.bold,
            color: Color(AppColors.textColor),
          ),
        ),
        const SizedBox(height: UIConstants.smallPadding),
        
        Row(
          children: [
            Expanded(
              child: TextFormField(
                initialValue: _analysisParams.riskFreeRate.toString(),
                decoration: const InputDecoration(
                  labelText: '無リスク利率',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final rate = double.tryParse(value);
                  if (rate != null) {
                    setState(() {
                      _analysisParams = AnalysisParams(
                        tickers: _analysisParams.tickers,
                        riskFreeRate: rate,
                        periodsPerYear: _analysisParams.periodsPerYear,
                        method: _analysisParams.method,
                      );
                    });
                  }
                },
              ),
            ),
            const SizedBox(width: UIConstants.smallPadding),
            Expanded(
              child: TextFormField(
                initialValue: _analysisParams.periodsPerYear.toString(),
                decoration: const InputDecoration(
                  labelText: '年間取引日数',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final periods = int.tryParse(value);
                  if (periods != null) {
                    setState(() {
                      _analysisParams = AnalysisParams(
                        tickers: _analysisParams.tickers,
                        riskFreeRate: _analysisParams.riskFreeRate,
                        periodsPerYear: periods,
                        method: _analysisParams.method,
                      );
                    });
                  }
                },
              ),
            ),
          ],
        ),
        
        const SizedBox(height: UIConstants.smallPadding),
        
        DropdownButtonFormField<String>(
          value: _analysisParams.method,
          decoration: const InputDecoration(
            labelText: 'リターン計算方法',
            border: OutlineInputBorder(),
          ),
          items: const [
            DropdownMenuItem(value: 'simple', child: Text('単純リターン')),
            DropdownMenuItem(value: 'log', child: Text('対数リターン')),
          ],
          onChanged: (value) {
            if (value != null) {
              setState(() {
                _analysisParams = AnalysisParams(
                  tickers: _analysisParams.tickers,
                  riskFreeRate: _analysisParams.riskFreeRate,
                  periodsPerYear: _analysisParams.periodsPerYear,
                  method: value,
                );
              });
            }
          },
        ),
      ],
    );
  }

  Widget _buildCorrelationParams() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '相関分析パラメータ',
          style: TextStyle(
            fontSize: TextStyles.body1Size,
            fontWeight: FontWeight.bold,
            color: Color(AppColors.textColor),
          ),
        ),
        const SizedBox(height: UIConstants.smallPadding),
        
        Row(
          children: [
            Expanded(
              child: TextFormField(
                initialValue: _correlationParams.correlationThreshold.toString(),
                decoration: const InputDecoration(
                  labelText: '相関閾値',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final threshold = double.tryParse(value);
                  if (threshold != null) {
                    setState(() {
                      _correlationParams = CorrelationParams(
                        tickers: _correlationParams.tickers,
                        method: _correlationParams.method,
                        correlationThreshold: threshold,
                        consolidationMethod: _correlationParams.consolidationMethod,
                      );
                    });
                  }
                },
              ),
            ),
            const SizedBox(width: UIConstants.smallPadding),
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _correlationParams.consolidationMethod,
                decoration: const InputDecoration(
                  labelText: '統合方法',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'mean', child: Text('平均')),
                  DropdownMenuItem(value: 'median', child: Text('中央値')),
                  DropdownMenuItem(value: 'first', child: Text('最初の資産')),
                ],
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _correlationParams = CorrelationParams(
                        tickers: _correlationParams.tickers,
                        method: _correlationParams.method,
                        correlationThreshold: _correlationParams.correlationThreshold,
                        consolidationMethod: value,
                      );
                    });
                  }
                },
              ),
            ),
          ],
        ),
        
        const SizedBox(height: UIConstants.smallPadding),
        
        DropdownButtonFormField<String>(
          value: _correlationParams.method,
          decoration: const InputDecoration(
            labelText: 'リターン計算方法',
            border: OutlineInputBorder(),
          ),
          items: const [
            DropdownMenuItem(value: 'simple', child: Text('単純リターン')),
            DropdownMenuItem(value: 'log', child: Text('対数リターン')),
          ],
          onChanged: (value) {
            if (value != null) {
              setState(() {
                _correlationParams = CorrelationParams(
                  tickers: _correlationParams.tickers,
                  method: value,
                  correlationThreshold: _correlationParams.correlationThreshold,
                  consolidationMethod: _correlationParams.consolidationMethod,
                );
              });
            }
          },
        ),
      ],
    );
  }

  Future<void> _runAnalysis() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      ApiResponse<String> response;
      
      switch (_currentView) {
        case 'summary':
          response = await AnalysisApi.getSummaryHtml(_analysisParams);
          break;
        case 'correlation':
          response = await AnalysisApi.getCorrelationHtml(_correlationParams);
          break;
        case 'consolidated':
          response = await AnalysisApi.getConsolidatedCorrelationHtml(_correlationParams);
          break;
        default:
          response = ApiResponse.error('不明な分析タイプ');
      }

      if (response.isSuccess) {
        setState(() {
          _htmlContent = response.data;
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
          _errorMessage = '分析の実行に失敗しました: $e';
        }
        _isLoading = false;
      });
    }
  }

  Widget _buildAnalysisArea() {
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
          ],
        ),
      );
    }

    if (_htmlContent == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.analytics,
              size: 64,
              color: Color(AppColors.textSecondaryColor),
            ),
            const SizedBox(height: UIConstants.largePadding),
            Text(
              '分析を実行してください',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                color: Color(AppColors.textSecondaryColor),
              ),
            ),
          ],
        ),
      );
    }

    // プラットフォーム固有の分析結果表示
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
              '分析結果表示',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            Text(
              '現在のプラットフォームでは、インタラクティブな分析結果の表示が制限されています。',
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
