import 'package:flutter/material.dart';
import '../api/download_api.dart';
import '../models/download.dart';
import '../models/common.dart';
import '../utils/constants.dart';

class DownloadScreen extends StatefulWidget {
  const DownloadScreen({super.key});

  @override
  State<DownloadScreen> createState() => _DownloadScreenState();
}

class _DownloadScreenState extends State<DownloadScreen> {
  final TextEditingController _symbolController = TextEditingController();
  final TextEditingController _startDateController = TextEditingController();
  final TextEditingController _endDateController = TextEditingController();
  DownloadParams _downloadParams = DownloadParams(symbol: '');
  List<FileInfo> _downloadedFiles = [];
  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void initState() {
    super.initState();
    _loadDownloadedFiles();
  }

  @override
  void dispose() {
    _symbolController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    super.dispose();
  }

  Future<void> _loadDownloadedFiles() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await DownloadApi.getAllFilesInfo();
      if (response.isSuccess) {
        setState(() {
          _downloadedFiles = response.data!.files;
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

  Future<void> _downloadData() async {
    if (_symbolController.text.trim().isEmpty) {
      setState(() {
        _errorMessage = 'ティッカーシンボルを入力してください';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final params = DownloadParams(
        symbol: _symbolController.text.trim(),
        startDate: _startDateController.text.trim().isNotEmpty 
            ? _startDateController.text.trim() 
            : null,
        endDate: _endDateController.text.trim().isNotEmpty 
            ? _endDateController.text.trim() 
            : null,
        providerName: _downloadParams.providerName,
        interval: _downloadParams.interval,
        prepost: _downloadParams.prepost,
      );

      final response = await DownloadApi.downloadStockData(params);
      if (response.isSuccess) {
        setState(() {
          _successMessage = 'データのダウンロードが完了しました';
          _isLoading = false;
        });
        _loadDownloadedFiles(); // ファイル一覧を更新
        _clearForm();
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
          _errorMessage = 'データのダウンロードに失敗しました: $e';
        }
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteFile(String filename) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await DownloadApi.deleteFile(filename);
      if (response.isSuccess) {
        setState(() {
          _successMessage = 'ファイルを削除しました';
          _isLoading = false;
        });
        _loadDownloadedFiles(); // ファイル一覧を更新
      } else {
        setState(() {
          _errorMessage = response.error;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'ファイルの削除に失敗しました: $e';
        _isLoading = false;
      });
    }
  }

  void _clearForm() {
    _symbolController.clear();
    _startDateController.clear();
    _endDateController.clear();
    setState(() {
      _downloadParams = DownloadParams(symbol: '');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildDownloadForm(),
          Expanded(
            child: _buildFileList(),
          ),
        ],
      ),
    );
  }

  Widget _buildDownloadForm() {
    return Card(
      margin: const EdgeInsets.all(UIConstants.defaultPadding),
      child: Padding(
        padding: const EdgeInsets.all(UIConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'データダウンロード',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            
            // ティッカーシンボル
            TextFormField(
              controller: _symbolController,
              decoration: const InputDecoration(
                labelText: 'ティッカーシンボル',
                hintText: '例: AAPL, MSFT, GOOGL',
                border: OutlineInputBorder(),
              ),
            ),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // 日付範囲
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _startDateController,
                    decoration: const InputDecoration(
                      labelText: '開始日',
                      hintText: 'YYYY-MM-DD',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: UIConstants.smallPadding),
                Expanded(
                  child: TextFormField(
                    controller: _endDateController,
                    decoration: const InputDecoration(
                      labelText: '終了日',
                      hintText: 'YYYY-MM-DD',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // プロバイダーとインターバル
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _downloadParams.providerName,
                    decoration: const InputDecoration(
                      labelText: 'データプロバイダー',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'yahoo', child: Text('Yahoo Finance')),
                    ],
                    onChanged: (value) {
                      if (value != null) {
                        setState(() {
                          _downloadParams = DownloadParams(
                            symbol: _downloadParams.symbol,
                            startDate: _downloadParams.startDate,
                            endDate: _downloadParams.endDate,
                            providerName: value,
                            interval: _downloadParams.interval,
                            prepost: _downloadParams.prepost,
                          );
                        });
                      }
                    },
                  ),
                ),
                const SizedBox(width: UIConstants.smallPadding),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _downloadParams.interval,
                    decoration: const InputDecoration(
                      labelText: 'インターバル',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: '1d', child: Text('日次')),
                      DropdownMenuItem(value: '1wk', child: Text('週次')),
                      DropdownMenuItem(value: '1mo', child: Text('月次')),
                    ],
                    onChanged: (value) {
                      if (value != null) {
                        setState(() {
                          _downloadParams = DownloadParams(
                            symbol: _downloadParams.symbol,
                            startDate: _downloadParams.startDate,
                            endDate: _downloadParams.endDate,
                            providerName: _downloadParams.providerName,
                            interval: value,
                            prepost: _downloadParams.prepost,
                          );
                        });
                      }
                    },
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: UIConstants.defaultPadding),
            
            // 実行ボタン
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _downloadData,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('データをダウンロード'),
              ),
            ),
            
            // メッセージ表示
            if (_errorMessage != null) ...[
              const SizedBox(height: UIConstants.smallPadding),
              Container(
                padding: const EdgeInsets.all(UIConstants.smallPadding),
                decoration: BoxDecoration(
                  color: Color(AppColors.errorColor).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(UIConstants.borderRadius),
                  border: Border.all(color: Color(AppColors.errorColor)),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.error_outline,
                      color: Color(AppColors.errorColor),
                      size: 20,
                    ),
                    const SizedBox(width: UIConstants.smallPadding),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: TextStyle(
                          color: Color(AppColors.errorColor),
                          fontSize: TextStyles.body2Size,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            
            if (_successMessage != null) ...[
              const SizedBox(height: UIConstants.smallPadding),
              Container(
                padding: const EdgeInsets.all(UIConstants.smallPadding),
                decoration: BoxDecoration(
                  color: Color(AppColors.successColor).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(UIConstants.borderRadius),
                  border: Border.all(color: Color(AppColors.successColor)),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.check_circle_outline,
                      color: Color(AppColors.successColor),
                      size: 20,
                    ),
                    const SizedBox(width: UIConstants.smallPadding),
                    Expanded(
                      child: Text(
                        _successMessage!,
                        style: TextStyle(
                          color: Color(AppColors.successColor),
                          fontSize: TextStyles.body2Size,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFileList() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_downloadedFiles.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.folder_open,
              size: 64,
              color: Color(AppColors.textSecondaryColor),
            ),
            const SizedBox(height: UIConstants.largePadding),
            Text(
              'ダウンロードされたファイルがありません',
              style: TextStyle(
                fontSize: TextStyles.headline3Size,
                color: Color(AppColors.textSecondaryColor),
              ),
            ),
            const SizedBox(height: UIConstants.defaultPadding),
            Text(
              '上記のフォームからデータをダウンロードしてください',
              style: TextStyle(
                fontSize: TextStyles.body1Size,
                color: Color(AppColors.textSecondaryColor),
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(UIConstants.defaultPadding),
      itemCount: _downloadedFiles.length,
      itemBuilder: (context, index) {
        final file = _downloadedFiles[index];
        return Card(
          margin: const EdgeInsets.only(bottom: UIConstants.smallPadding),
          child: ListTile(
            leading: Icon(
              Icons.insert_drive_file,
              color: Color(AppColors.primaryColor),
            ),
            title: Text(
              file.filename,
              style: TextStyle(
                fontSize: TextStyles.body1Size,
                fontWeight: FontWeight.bold,
                color: Color(AppColors.textColor),
              ),
            ),
            subtitle: Text(
              'サイズ: ${file.sizeReadable}',
              style: TextStyle(
                fontSize: TextStyles.body2Size,
                color: Color(AppColors.textSecondaryColor),
              ),
            ),
            trailing: IconButton(
              icon: Icon(
                Icons.delete,
                color: Color(AppColors.errorColor),
              ),
              onPressed: () => _showDeleteDialog(file.filename),
            ),
          ),
        );
      },
    );
  }

  void _showDeleteDialog(String filename) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('ファイル削除'),
          content: Text('$filename を削除しますか？'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('キャンセル'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _deleteFile(filename);
              },
              style: TextButton.styleFrom(
                foregroundColor: Color(AppColors.errorColor),
              ),
              child: const Text('削除'),
            ),
          ],
        );
      },
    );
  }
}
