import 'package:flutter/material.dart';
import '../api/portfolio_api.dart';
import '../models/portfolio.dart';
import '../utils/constants.dart';

class PortfolioScreen extends StatefulWidget {
  const PortfolioScreen({super.key});

  @override
  State<PortfolioScreen> createState() => _PortfolioScreenState();
}

class _PortfolioScreenState extends State<PortfolioScreen> {
  PortfolioParams _portfolioParams = PortfolioParams();
  String? _htmlContent;
  bool _isLoading = false;
  String? _errorMessage;
  String _currentView = 'optimization'; // 'optimization', 'efficient_frontier'

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildControlPanel(),
          Expanded(
            child: _buildPortfolioArea(),
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
              'ポートフォリオ設定',
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
                  child: _buildPortfolioTypeButton('最適化', 'optimization'),
                ),
                const SizedBox(width: UIConstants.smallPadding),
                Expanded(
                  child: _buildPortfolioTypeButton('効率的フロンティア', 'efficient_frontier'),
                ),
              ],
            ),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // パラメータ設定
            _buildPortfolioParams(),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // 実行ボタン
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _runPortfolioAnalysis,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('ポートフォリオ分析実行'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPortfolioTypeButton(String label, String type) {
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

  Widget _buildPortfolioParams() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ポートフォリオパラメータ',
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
                initialValue: _portfolioParams.riskFreeRate.toString(),
                decoration: const InputDecoration(
                  labelText: '無リスク利率',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final rate = double.tryParse(value);
                  if (rate != null) {
                    setState(() {
                      _portfolioParams = PortfolioParams(
                        tickers: _portfolioParams.tickers,
                        riskFreeRate: rate,
                        periodsPerYear: _portfolioParams.periodsPerYear,
                        method: _portfolioParams.method,
                        optimizationMethod: _portfolioParams.optimizationMethod,
                        targetReturn: _portfolioParams.targetReturn,
                        targetRisk: _portfolioParams.targetRisk,
                        riskTolerance: _portfolioParams.riskTolerance,
                        maxWeight: _portfolioParams.maxWeight,
                        minWeight: _portfolioParams.minWeight,
                      );
                    });
                  }
                },
              ),
            ),
            const SizedBox(width: UIConstants.smallPadding),
            Expanded(
              child: TextFormField(
                initialValue: _portfolioParams.periodsPerYear.toString(),
                decoration: const InputDecoration(
                  labelText: '年間取引日数',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final periods = int.tryParse(value);
                  if (periods != null) {
                    setState(() {
                      _portfolioParams = PortfolioParams(
                        tickers: _portfolioParams.tickers,
                        riskFreeRate: _portfolioParams.riskFreeRate,
                        periodsPerYear: periods,
                        method: _portfolioParams.method,
                        optimizationMethod: _portfolioParams.optimizationMethod,
                        targetReturn: _portfolioParams.targetReturn,
                        targetRisk: _portfolioParams.targetRisk,
                        riskTolerance: _portfolioParams.riskTolerance,
                        maxWeight: _portfolioParams.maxWeight,
                        minWeight: _portfolioParams.minWeight,
                      );
                    });
                  }
                },
              ),
            ),
          ],
        ),
        
        const SizedBox(height: UIConstants.smallPadding),
        
        Row(
          children: [
            Expanded(
              child: TextFormField(
                initialValue: _portfolioParams.targetReturn?.toString() ?? '',
                decoration: const InputDecoration(
                  labelText: '目標リターン',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final targetReturn = double.tryParse(value);
                  setState(() {
                    _portfolioParams = PortfolioParams(
                      tickers: _portfolioParams.tickers,
                      riskFreeRate: _portfolioParams.riskFreeRate,
                      periodsPerYear: _portfolioParams.periodsPerYear,
                      method: _portfolioParams.method,
                      optimizationMethod: _portfolioParams.optimizationMethod,
                      targetReturn: targetReturn,
                      targetRisk: _portfolioParams.targetRisk,
                      riskTolerance: _portfolioParams.riskTolerance,
                      maxWeight: _portfolioParams.maxWeight,
                      minWeight: _portfolioParams.minWeight,
                    );
                  });
                },
              ),
            ),
            const SizedBox(width: UIConstants.smallPadding),
            Expanded(
              child: TextFormField(
                initialValue: _portfolioParams.targetRisk?.toString() ?? '',
                decoration: const InputDecoration(
                  labelText: '目標リスク',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final targetRisk = double.tryParse(value);
                  setState(() {
                    _portfolioParams = PortfolioParams(
                      tickers: _portfolioParams.tickers,
                      riskFreeRate: _portfolioParams.riskFreeRate,
                      periodsPerYear: _portfolioParams.periodsPerYear,
                      method: _portfolioParams.method,
                      optimizationMethod: _portfolioParams.optimizationMethod,
                      targetReturn: _portfolioParams.targetReturn,
                      targetRisk: targetRisk,
                      riskTolerance: _portfolioParams.riskTolerance,
                      maxWeight: _portfolioParams.maxWeight,
                      minWeight: _portfolioParams.minWeight,
                    );
                  });
                },
              ),
            ),
          ],
        ),
        
        const SizedBox(height: UIConstants.smallPadding),
        
        Row(
          children: [
            Expanded(
              child: TextFormField(
                initialValue: _portfolioParams.maxWeight.toString(),
                decoration: const InputDecoration(
                  labelText: '最大ウェイト',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final maxWeight = double.tryParse(value);
                  if (maxWeight != null) {
                    setState(() {
                      _portfolioParams = PortfolioParams(
                        tickers: _portfolioParams.tickers,
                        riskFreeRate: _portfolioParams.riskFreeRate,
                        periodsPerYear: _portfolioParams.periodsPerYear,
                        method: _portfolioParams.method,
                        optimizationMethod: _portfolioParams.optimizationMethod,
                        targetReturn: _portfolioParams.targetReturn,
                        targetRisk: _portfolioParams.targetRisk,
                        riskTolerance: _portfolioParams.riskTolerance,
                        maxWeight: maxWeight,
                        minWeight: _portfolioParams.minWeight,
                      );
                    });
                  }
                },
              ),
            ),
            const SizedBox(width: UIConstants.smallPadding),
            Expanded(
              child: TextFormField(
                initialValue: _portfolioParams.minWeight.toString(),
                decoration: const InputDecoration(
                  labelText: '最小ウェイト',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  final minWeight = double.tryParse(value);
                  if (minWeight != null) {
                    setState(() {
                      _portfolioParams = PortfolioParams(
                        tickers: _portfolioParams.tickers,
                        riskFreeRate: _portfolioParams.riskFreeRate,
                        periodsPerYear: _portfolioParams.periodsPerYear,
                        method: _portfolioParams.method,
                        optimizationMethod: _portfolioParams.optimizationMethod,
                        targetReturn: _portfolioParams.targetReturn,
                        targetRisk: _portfolioParams.targetRisk,
                        riskTolerance: _portfolioParams.riskTolerance,
                        maxWeight: _portfolioParams.maxWeight,
                        minWeight: minWeight,
                      );
                    });
                  }
                },
              ),
            ),
          ],
        ),
        
        const SizedBox(height: UIConstants.smallPadding),
        
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _portfolioParams.method,
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
                      _portfolioParams = PortfolioParams(
                        tickers: _portfolioParams.tickers,
                        riskFreeRate: _portfolioParams.riskFreeRate,
                        periodsPerYear: _portfolioParams.periodsPerYear,
                        method: value,
                        optimizationMethod: _portfolioParams.optimizationMethod,
                        targetReturn: _portfolioParams.targetReturn,
                        targetRisk: _portfolioParams.targetRisk,
                        riskTolerance: _portfolioParams.riskTolerance,
                        maxWeight: _portfolioParams.maxWeight,
                        minWeight: _portfolioParams.minWeight,
                      );
                    });
                  }
                },
              ),
            ),
            const SizedBox(width: UIConstants.smallPadding),
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _portfolioParams.optimizationMethod,
                decoration: const InputDecoration(
                  labelText: '最適化方法',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'sharpe', child: Text('シャープレシオ')),
                  DropdownMenuItem(value: 'min_variance', child: Text('最小分散')),
                  DropdownMenuItem(value: 'max_return', child: Text('最大リターン')),
                ],
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      _portfolioParams = PortfolioParams(
                        tickers: _portfolioParams.tickers,
                        riskFreeRate: _portfolioParams.riskFreeRate,
                        periodsPerYear: _portfolioParams.periodsPerYear,
                        method: _portfolioParams.method,
                        optimizationMethod: value,
                        targetReturn: _portfolioParams.targetReturn,
                        targetRisk: _portfolioParams.targetRisk,
                        riskTolerance: _portfolioParams.riskTolerance,
                        maxWeight: _portfolioParams.maxWeight,
                        minWeight: _portfolioParams.minWeight,
                      );
                    });
                  }
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  Future<void> _runPortfolioAnalysis() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = _currentView == 'optimization'
          ? await PortfolioApi.getOptimizationHtml(_portfolioParams)
          : await PortfolioApi.getEfficientFrontierHtml(_portfolioParams);

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
          _errorMessage = 'ポートフォリオ分析の実行に失敗しました: $e';
        }
        _isLoading = false;
      });
    }
  }

  Widget _buildPortfolioArea() {
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
              Icons.pie_chart,
              size: 64,
              color: Color(AppColors.textSecondaryColor),
            ),
            const SizedBox(height: UIConstants.largePadding),
            Text(
              'ポートフォリオ分析を実行してください',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                color: Color(AppColors.textSecondaryColor),
              ),
            ),
          ],
        ),
      );
    }

    // プラットフォーム固有のポートフォリオ結果表示
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
              'ポートフォリオ結果表示',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            Text(
              '現在のプラットフォームでは、インタラクティブなポートフォリオ結果の表示が制限されています。',
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
