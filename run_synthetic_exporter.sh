#!/bin/bash
# Synthetic Browser監視結果エクスポーター実行スクリプト
# 作成日: 2025-05-26

echo "Synthetic Browser監視結果エクスポーター"
echo "67個の動作確認済みメトリクスを活用した包括的データエクスポート"
echo

# 環境変数確認
if [ ! -f ".env" ]; then
    echo ".envファイルが見つかりません"
    echo "DT_API_TOKEN と DT_ENV_URL を設定してください"
    exit 1
fi

# ログディレクトリ作成
mkdir -p .logs

# 使用方法表示
echo "使用可能なオプション:"
echo "  --tag Owner:Koizumi    # タグフィルタ"
echo "  --hours 48             # 取得期間（時間）"
echo "  --resolution 30m       # データ解像度"
echo "  --output my_results    # 出力ファイル名"
echo "  --no-geo              # 地理的メトリクス除外"
echo

# 引数がある場合は引数付きで実行、ない場合はデフォルト実行
if [ $# -eq 0 ]; then
    echo "デフォルト実行中（過去24時間、全メトリクス）..."
    python3 synthetic_browser_exporter.py
else
    echo "カスタム設定で実行中..."
    echo "引数: $@"
    python3 synthetic_browser_exporter.py "$@"
fi

# 結果確認
if [ $? -eq 0 ]; then
    echo
    echo "エクスポート完了"
    echo
    echo "生成されたファイル:"
    ls -la output/ultimate_browser_results_*.csv 2>/dev/null
    echo
    ls -la output/ultimate_browser_results_*_summary.json 2>/dev/null
    echo
    echo "ログファイル:"
    ls -la .logs/ultimate_browser_export_*.log 2>/dev/null
    echo
    echo "次のステップ:"
    echo "  1. CSVファイルをExcelで開いて分析"
    echo "  2. サマリーJSONで全体概要を確認"  
    echo "  3. 特定タグでフィルタリング実行"
    echo "     例: python3 synthetic_browser_exporter.py --tag Owner:Koizumi"
else
    echo
    echo "エクスポート失敗"
    echo "ログファイルを確認してください:"
    ls -la .logs/ultimate_browser_export_*.log 2>/dev/null
fi 