import 'package:flutter/material.dart';
import 'utils/constants.dart';
import 'api/api_client.dart';
import 'screens/chart_screen.dart';
import 'screens/analysis_screen.dart';
import 'screens/portfolio_screen.dart';
import 'screens/download_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  runApp(const NewAnalyzerApp());
}

// バックエンドサーバーの状態を確認
Future<void> checkServerStatus() async {
  try {
    final isAvailable = await ApiClient.isServerAvailable();
    if (!isAvailable) {
      // サーバーが利用できない場合の処理
    }
  } catch (e) {
    // エラーが発生した場合の処理
  }
}

class NewAnalyzerApp extends StatelessWidget {
  const NewAnalyzerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NewAnalyzer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Color(AppColors.primaryColor),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(AppColors.primaryColor),
          foregroundColor: Colors.white,
          elevation: 2,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(AppColors.primaryColor),
            foregroundColor: Colors.white,
            minimumSize: const Size(double.infinity, UIConstants.buttonHeight),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(UIConstants.borderRadius),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(UIConstants.borderRadius),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: UIConstants.defaultPadding,
            vertical: UIConstants.smallPadding,
          ),
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(UIConstants.borderRadius),
          ),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  static final List<Widget> _screens = [
    const ChartScreen(),
    const AnalysisScreen(),
    const PortfolioScreen(),
    const DownloadScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NewAnalyzer'),
        centerTitle: true,
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.show_chart),
            label: 'チャート',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: '分析',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.pie_chart),
            label: 'ポートフォリオ',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.download),
            label: 'ダウンロード',
          ),
        ],
      ),
    );
  }
}

class PlaceholderScreen extends StatelessWidget {
  final String title;
  final IconData icon;

  const PlaceholderScreen({
    super.key,
    required this.title,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 80,
            color: Color(AppColors.textSecondaryColor),
          ),
          const SizedBox(height: UIConstants.largePadding),
          Text(
            title,
            style: TextStyle(
              fontSize: TextStyles.headline1Size,
              color: Color(AppColors.textColor),
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: UIConstants.defaultPadding),
          Text(
            'この機能は現在開発中です',
            style: TextStyle(
              fontSize: TextStyles.body1Size,
              color: Color(AppColors.textSecondaryColor),
            ),
          ),
          const SizedBox(height: UIConstants.largePadding),
          ElevatedButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('$title機能は準備中です'),
                  backgroundColor: Color(AppColors.warningColor),
                ),
              );
            },
            child: const Text('機能を確認'),
          ),
        ],
      ),
    );
  }
}
