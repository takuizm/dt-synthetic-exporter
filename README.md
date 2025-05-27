# Dynatrace Synthetic Browser監視データエクスポーター
**プロフェッショナル・ガイド：環境構築から運用まで**  
作成日: 2025-01-27  
バージョン: 2.1

## 概要

このツールは、Dynatrace のSynthetic Browser監視データをCSVファイルにエクスポートし、Excel等での詳細分析を可能にするツールです。67種類のパフォーマンスメトリクスを自動収集し、Webサイトの性能分析レポートを生成します。

### 適用範囲
- Webサイトのパフォーマンスを定期的に分析する業務
- Dynatrace データのExcel詳細分析
- 複数監視結果の一括確認・レポート作成
- 技術的詳細を不要とする分析業務

### 対応環境
- **macOS**: macOS 10.14以上
- **Windows**: Windows 10以上 
- **Linux**: Ubuntu 18.04以上

### 取得データ
- **Core Web Vitals**: LCP、CLS（Google推奨指標）
- **ページパフォーマンス**: ロード時間、Speed Index、表示完了時間
- **ネットワーク分析**: TTFB、レスポンス時間、サーバー負荷
- **可用性データ**: 成功率、失敗率、地域別データ

---

## 環境構築

### 前提条件

#### Python環境の確認

**macOS:**
```bash
# ターミナルを開いて実行
python3 --version
```

**Windows:**
```cmd
# コマンドプロンプトを開いて実行
python --version
```

Python 3.8以上が表示されることを確認してください。インストールされていない場合は[Python公式サイト](https://www.python.org/downloads/)からダウンロード・インストールを行ってください。

#### 必要ファイルの確認
以下のファイルが含まれていることを確認してください：
- `README.md`（このファイル）
- `synthetic_browser_exporter.py`
- `requirements.txt`
- `run_synthetic_exporter.sh`
- `.env.template`

### インストール手順

#### 1. プロジェクトディレクトリへの移動

**macOS:**
```bash
cd ~/Downloads/dt-synthetic-exporter
ls -la  # ファイル存在確認
```

**Windows:**
```cmd
cd %USERPROFILE%\Downloads\dt-synthetic-exporter
dir     # ファイル存在確認
```

#### 2. 依存ライブラリのインストール

**macOS:**
```bash
pip3 install -r requirements.txt
python3 -c "import requests, pandas; print('インストール完了')"
```

**Windows:**
```cmd
pip install -r requirements.txt
python -c "import requests, pandas; print('インストール完了')"
```

#### 3. Dynatrace API設定

##### APIトークンの取得
1. Dynatrace環境にログイン
2. Settings → Integration → Dynatrace API → API tokens
3. Generate tokenをクリック
4. Token name: `SyntheticExporter`等の識別可能な名前を設定
5. 必要な権限を付与：
   - `Read synthetic monitors`
   - `Read metrics`
   - `Read entities`
6. Generateをクリックし、トークンを安全に保存

##### 環境設定ファイルの作成

**macOS:**
```bash
cp .env.template .env
open .env
```

**Windows:**
```cmd
copy .env.template .env
notepad .env
```

テキストエディタで以下のように編集してください：
```
DT_API_TOKEN=取得したAPIトークン
DT_ENV_URL=https://あなたのテナント.dynatrace.com
```

注意事項：
- 等号（=）の前後にスペースを入れない
- クォートは使用しない
- APIトークンとURLは正確に入力

#### 4. 動作確認

**macOS:**
```bash
chmod +x run_synthetic_exporter.sh
python3 synthetic_browser_exporter.py --hours 1
```

**Windows:**
```cmd
python synthetic_browser_exporter.py --hours 1
```

正常に動作する場合、`output/`ディレクトリにCSVファイルが生成されます。

---

## 基本的な使用方法

### 標準実行

**最も基本的な実行（推奨）:**
```bash
# macOS
./run_synthetic_exporter.sh

# Windows
python synthetic_browser_exporter.py
```

過去72時間のデータを取得し、結果をCSVファイルとして出力します。

### 出力ファイル

実行完了後、`output/`ディレクトリに以下のファイルが生成されます：

- **`ultimate_browser_results_YYYYMMDD_HHMMSS.csv`**: 詳細データ（Excel分析用）
- **`ultimate_browser_results_YYYYMMDD_HHMMSS_summary.json`**: 統計サマリー

### 結果確認

**macOS:**
```bash
open output/ultimate_browser_results_*.csv
```

**Windows:**
```cmd
start output\ultimate_browser_results_*.csv
```

---

## 応用的な使用方法

### よく使用されるオプション

#### 期間指定
```bash
python3 synthetic_browser_exporter.py --hours 24    # 過去24時間
python3 synthetic_browser_exporter.py --hours 168   # 過去1週間
```

#### タグフィルタリング
```bash
python3 synthetic_browser_exporter.py --tag Owner:TeamName
python3 synthetic_browser_exporter.py --tag Environment:Production
```

#### データ解像度設定
```bash
python3 synthetic_browser_exporter.py --resolution 15m   # 15分間隔
python3 synthetic_browser_exporter.py --resolution 1h    # 1時間間隔
```

#### 監視別詳細分析
```bash
python3 synthetic_browser_exporter.py --monitor-analysis
```

#### 高速化オプション
```bash
python3 synthetic_browser_exporter.py --no-geo  # 地域データ除外
```

### 定期レポート作成例

#### 日次レポート
```bash
python3 synthetic_browser_exporter.py \
  --hours 24 \
  --resolution 1h \
  --output daily_report_$(date +%Y%m%d)
```

#### 週次詳細分析
```bash
python3 synthetic_browser_exporter.py \
  --tag Environment:Production \
  --hours 168 \
  --resolution 30m \
  --output weekly_analysis \
  --monitor-analysis
```

---

## データ分析

### CSVファイルの主要カラム

| カラム名 | 内容 | 用途 |
|---------|------|------|
| `timestamp` | 測定日時 | 時系列分析 |
| `monitor_name` | 監視名 | 監視別フィルタリング |
| `monitor_url` | 監視対象URL | 対象サイト確認 |
| `metric_display_name` | メトリクス名 | 指標種別確認 |
| `value` | 測定値 | 分析対象データ |
| `unit` | 単位 | 数値の解釈 |

### 性能評価基準

#### 良好な範囲
- **ページロード時間**: 3.0秒以下
- **LCP（最大コンテンツ描画）**: 2.5秒以下
- **CLS（レイアウトシフト）**: 0.1以下
- **可用性**: 99%以上

#### 注意が必要な範囲
- **ページロード時間**: 3.0〜5.0秒
- **LCP**: 2.5〜4.0秒
- **CLS**: 0.1〜0.25
- **可用性**: 95〜99%

#### 改善が必要な範囲
- **ページロード時間**: 5.0秒超
- **LCP**: 4.0秒超
- **CLS**: 0.25超
- **可用性**: 95%未満

### Excel分析の基本手順

詳細な分析方法については `docs/分析方法ガイド_20250127_v1.md` を参照してください。

1. CSVファイルをExcelで開く
2. データをテーブル形式に変換
3. フィルター機能を使用して対象データを絞り込み
4. 時系列グラフを作成してトレンド分析を実施
5. 監視別比較分析を実行

---

## トラブルシューティング

### よくある問題と解決方法

#### 「環境変数が設定されていません」
**原因**: `.env`ファイルの設定に問題があります  
**解決方法**: 
1. `.env`ファイルの存在確認
2. APIトークンとURLの正確性確認
3. ファイル保存の確認

#### 「データが取得できませんでした」
**原因**: API接続またはBrowser監視の設定に問題があります  
**解決方法**:
1. APIトークンの権限確認
2. DynatraceテナントURLの確認
3. ネットワーク接続の確認

#### 「ライブラリがインストールできない」
**原因**: Python環境またはネットワークの問題です  
**解決方法**:
```bash
pip3 install --upgrade pip
pip3 install requests pandas python-dotenv pytz
```

#### 「Permission denied」
**原因**: 実行権限の問題です  
**解決方法**:
```bash
chmod +x run_synthetic_exporter.sh
```

### ログファイルの確認

エラーの詳細は `.logs/` ディレクトリ内のログファイルで確認できます：
```bash
tail -20 .logs/ultimate_browser_export_*.log
```

---

## 運用推奨パターン

### 定期監視
```bash
# 毎日の性能チェック
python3 synthetic_browser_exporter.py --hours 24 --resolution 1h

# 週次詳細レポート
python3 synthetic_browser_exporter.py --hours 168 --resolution 30m --monitor-analysis
```

### 問題調査
```bash
# 高解像度データでの詳細調査
python3 synthetic_browser_exporter.py --hours 6 --resolution 5m
```

### 特定環境監視
```bash
# 本番環境のみ
python3 synthetic_browser_exporter.py --tag Environment:Production

# 特定チーム担当監視のみ
python3 synthetic_browser_exporter.py --tag Owner:TeamName
```

---

## サポート

### 問い合わせ前の確認事項
1. 最新のログファイル内容の確認
2. `.env`ファイル設定の再確認  
3. Dynatrace環境への接続確認
4. Pythonとライブラリのバージョン確認

### デバッグ実行
詳細なエラー情報が必要な場合：
```bash
python3 synthetic_browser_exporter.py --hours 1 2>&1 | tee debug_output.txt
```

---

## まとめ

本ツールにより、Dynatrace Synthetic Browser監視の67種類のメトリクスを効率的にExcel分析可能な形式で取得できます。定期的な性能監視、詳細な問題分析、包括的なレポート作成に活用してください。

基本的な実行方法を習得後、業務要件に応じてオプションパラメータを活用し、効果的なWebサイト性能分析を実施してください。 