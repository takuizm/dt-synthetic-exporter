# Dynatrace Synthetic Browser監視データエクスポーター
**利用ガイド：環境構築から運用まで**  
作成日: 2025-05-27  
バージョン: 1.0

## 概要

このツールは、Dynatrace のSynthetic Browser監視データをCSVファイルにエクスポートし、Excel等での詳細分析を可能にするツールです。最大67種類のパフォーマンスメトリクスを自動収集し、Webサイトの性能分析レポートを生成します。

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

## プロジェクト構造

```
dt-synthetic-exporter/
├── README.md                                 # メインガイド（このファイル）
│                                             #     67種類メトリクス詳細・使用方法・分析手法
├── synthetic_browser_exporter.py             # メインプログラム
│                                             #     Dynatrace APIからデータ取得・CSV出力
├── metrics_analyzer.py                       # メトリクス分析ツール（基本的に使用しません）
│                                             #     公式メトリクス vs 実際取得の比較・診断
├── run_synthetic_exporter.sh                 # 実行スクリプト（macOS/Linux）
├── run_synthetic_exporter.bat                # 実行スクリプト（Windows）
├── requirements.txt                          # 依存ライブラリ一覧
├── .env.template                             # 環境設定テンプレート
├── .env                                      # 環境設定ファイル（作成後）
│                                             #     APIトークン・テナントURL設定
├── docs/                                     # 技術ドキュメント
│   └── 技術仕様_20250127.md                  #     API制約・実行実績・トラブルシューティング
├── output/                                   # 実行結果（自動生成）
│   ├── ultimate_browser_results_*.csv        #     詳細データ（Excel分析用）
│   ├── *_monitor_analysis.csv                #     監視別分析データ（推奨）
│   ├── *_summary.json                        #     統計サマリー
│   └── *_monitor_analysis.json               #     監視別詳細分析結果
└── .logs/                                    # 実行ログ（自動生成）
    └── ultimate_browser_export_*.log         #     デバッグ・トラブルシューティング用
```

### ファイル役割詳細

#### **必須ファイル（実行に必要）**
- **`synthetic_browser_exporter.py`**: メインプログラム、データ取得・変換・出力
- **`requirements.txt`**: Python依存ライブラリ（requests, pandas等）
- **`.env`**: API認証情報（作成が必要）

#### **実行支援ファイル**
- **`run_synthetic_exporter.sh/.bat`**: ワンクリック実行用スクリプト
- **`.env.template`**: 環境設定の雛形

#### **分析・診断ツール**
- **`metrics_analyzer.py`**: 環境診断、メトリクス取得状況の確認
- **`README.md`**: 完全ガイド、67種類メトリクス詳細リファレンス

#### **技術情報**
- **`docs/技術仕様_20250127.md`**: API制約、実行実績、トラブルシューティング

#### **自動生成ディレクトリ**
- **`output/`**: CSV・JSON出力ファイル（実行時に自動作成）
- **`.logs/`**: 実行ログファイル（デバッグ用、自動作成）

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
プロジェクト構造で示した以下の必須ファイルが含まれていることを確認してください：

**必須ファイル:**
- `README.md`（このファイル）
- `synthetic_browser_exporter.py`（メインプログラム）
- `requirements.txt`（依存ライブラリ）
- `run_synthetic_exporter.sh`（実行スクリプト・macOS/Linux）
- `run_synthetic_exporter.bat`（実行スクリプト・Windows）
- `.env.template`（環境設定テンプレート）

**分析ツール:**
- `metrics_analyzer.py`（メトリクス分析・診断ツール）

**技術ドキュメント:**
- `docs/技術仕様_20250127.md`（API制約・トラブルシューティング）

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

#### **標準出力**
- **`ultimate_browser_results_YYYYMMDD_HHMMSS.csv`**: 詳細データ（Excel分析用）
- **`ultimate_browser_results_YYYYMMDD_HHMMSS_summary.json`**: 統計サマリー

#### **監視別分析出力（`--monitor-analysis`使用時）**
- **`ultimate_browser_results_YYYYMMDD_HHMMSS_monitor_analysis.csv`**: 監視別グルーピング済みデータ（**最も使いやすい**）
- **`ultimate_browser_results_YYYYMMDD_HHMMSS_monitor_summary.csv`**: 監視別統計サマリー
- **`ultimate_browser_results_YYYYMMDD_HHMMSS_monitor_analysis.json`**: 監視別詳細分析結果

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

#### 監視別詳細分析（**推奨**）
```bash
python3 synthetic_browser_exporter.py --monitor-analysis
```

**`--monitor-analysis`オプションの特徴:**
- **監視別にグルーピング**: 各監視の全メトリクスが1つのセクションにまとまる
- **統計情報付き**: 平均値、最大値、最小値、標準偏差を自動計算
- **Excel分析に最適**: フィルタリングや比較分析が容易
- **レポート作成向け**: 監視別の性能評価が一目で分かる

#### 高速化オプション
```bash
python3 synthetic_browser_exporter.py --no-geo  # 地域データ除外
```

### 定期レポート作成例

#### 日次レポート（監視別分析付き）
```bash
python3 synthetic_browser_exporter.py \
  --hours 24 \
  --resolution 1h \
  --monitor-analysis \
  --output daily_report_$(date +%Y%m%d)
```

#### 週次詳細分析
```bash
python3 synthetic_browser_exporter.py \
  --tag Environment:Production \
  --hours 168 \
  --resolution 30m \
  --monitor-analysis \
  --output weekly_analysis
```

#### 本番環境監視レポート
```bash
python3 synthetic_browser_exporter.py \
  --tag Environment:Production \
  --hours 24 \
  --resolution 15m \
  --monitor-analysis \
  --no-geo
```

---

## データ分析

### CSVファイルの主要カラム

#### **標準CSV**
| カラム名 | 内容 | 用途 |
|---------|------|------|
| `timestamp` | 測定日時 | 時系列分析 |
| `monitor_name` | 監視名 | 監視別フィルタリング |
| `monitor_url` | 監視対象URL | 対象サイト確認 |
| `metric_display_name` | メトリクス名 | 指標種別確認 |
| `value` | 測定値 | 分析対象データ |
| `unit` | 単位 | 数値の解釈 |

#### **監視別分析CSV（`--monitor-analysis`）**
| カラム名 | 内容 | 用途 |
|---------|------|------|
| `monitor_name` | 監視名 | 監視識別 |
| `monitor_url` | 監視対象URL | 対象サイト確認 |
| `metric_category` | メトリクスカテゴリ | 分析分類 |
| `metric_name` | メトリクス名 | 指標種別確認 |
| `avg_value` | 平均値 | 基本性能指標 |
| `max_value` | 最大値 | 最悪ケース確認 |
| `min_value` | 最小値 | 最良ケース確認 |
| `std_value` | 標準偏差 | 安定性評価 |
| `measurement_count` | 測定回数 | データ信頼性 |

#### **統計値の算出方法と活用指針**

##### **算出方法**
各統計値は、指定期間内の全測定データポイントから以下の方法で算出されます：

| 統計値 | 算出方法 | 計算式 |
|--------|----------|--------|
| **平均値** (`avg_value`) | 算術平均 | `Σ(全測定値) ÷ 測定回数` |
| **最大値** (`max_value`) | 期間内最大値 | `max(全測定値)` |
| **最小値** (`min_value`) | 期間内最小値 | `min(全測定値)` |
| **標準偏差** (`std_value`) | 母集団標準偏差 | `√(Σ(測定値-平均値)² ÷ 測定回数)` |
| **測定回数** (`measurement_count`) | データポイント数 | `count(有効な測定値)` |

##### **活用指針**

| 統計値 | 主要用途 | 評価基準 | 注意点 |
|--------|----------|----------|--------|
| **平均値** | 基本性能評価 | 性能評価基準と比較 | 外れ値の影響を受けやすい |
| **最大値** | 最悪ケース分析 | SLA違反リスク評価 | 一時的な異常値の可能性 |
| **最小値** | 最良ケース確認 | 理想的な性能の把握 | キャッシュ効果等の影響 |
| **標準偏差** | 安定性評価 | 平均値の10-20%以下が理想 | 値が大きいほど不安定 |
| **測定回数** | データ信頼性 | 30回以上で統計的に有意 | 少ないと信頼性低下 |

##### **実践的な分析例**

**例：ページロード時間の分析**
```
monitor_name: "本番サイト監視"
metric_name: "actionDuration.load"
avg_value: 2800ms
max_value: 8500ms  
min_value: 1200ms
std_value: 950ms
measurement_count: 144
```

**分析結果**:
- **平均性能**: 2.8秒（良好範囲）
- **最悪ケース**: 8.5秒（要改善レベル）
- **安定性**: 標準偏差950ms（平均値の34%）→ やや不安定
- **データ信頼性**: 144回測定（十分な信頼性）

**改善提案**:
1. 最大値が平均値の3倍以上 → 異常値調査が必要
2. 標準偏差が大きい → 性能の安定化対策が必要
3. 測定回数が十分 → 統計的に信頼できる結果

##### **Excel分析での活用方法**

1. **性能ランキング**: `avg_value`列でソートし、監視別性能比較
2. **安定性評価**: `std_value ÷ avg_value`で変動係数を算出
3. **異常値検知**: `max_value - avg_value > 2 × std_value`で外れ値特定
4. **信頼性フィルタ**: `measurement_count ≥ 30`で信頼できるデータのみ抽出
5. **条件付き書式**: 
   - 平均値：性能評価基準で色分け
   - 標準偏差：平均値の20%以上で警告色
   - 測定回数：30未満で注意色

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

#### **標準CSVの場合**
1. **データ準備**: CSVファイルをExcelで開き、テーブル形式に変換
2. **フィルタリング**: timestamp、metric_display_name、monitor_name列でデータを絞り込み
3. **統計分析**: 平均値、最大値、最小値、標準偏差を算出
4. **条件付き書式**: 評価基準に基づく色分け（良好=緑、注意=黄、要改善=赤）
5. **時系列グラフ**: トレンド分析とパフォーマンス変化の可視化

#### **監視別分析CSVの場合（推奨）**
1. **データ準備**: monitor_analysis.csvをExcelで開き、テーブル形式に変換
2. **信頼性フィルタ**: measurement_count ≥ 30でフィルタリング（統計的信頼性確保）
3. **性能ランキング**: avg_value列でソートし、監視別性能比較
4. **変動係数算出**: 新列作成 `=std_value/avg_value` で安定性指標を計算
5. **異常値検知**: 新列作成 `=IF(max_value-avg_value>2*std_value,"要調査","正常")` で外れ値特定
6. **条件付き書式適用**:
   - avg_value：性能評価基準で色分け（良好=緑、注意=黄、要改善=赤）
   - 変動係数：0.2以上で警告色（不安定な性能）
   - measurement_count：30未満で注意色（信頼性不足）
7. **カテゴリ別分析**: metric_category列でピボットテーブル作成
8. **ダッシュボード作成**: 監視別サマリーと異常値アラートを統合

---

## トラブルシューティング

### よくある問題と解決方法

#### "環境変数が設定されていません"
**原因**: `.env`ファイルの設定に問題があります  
**解決方法**: 
1. `.env`ファイルの存在確認
2. APIトークンとURLの正確性確認
3. ファイル保存の確認

#### "データが取得できませんでした"
**原因**: API接続またはBrowser監視の設定に問題があります  
**解決方法**:
1. APIトークンの権限確認
2. DynatraceテナントURLの確認
3. ネットワーク接続の確認

#### "ライブラリがインストールできない"
**原因**: Python環境またはネットワークの問題です  
**解決方法**:
```bash
pip3 install --upgrade pip
pip3 install requests pandas python-dotenv pytz
```

#### "Permission denied"
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
# 毎日の性能チェック（監視別分析付き）
python3 synthetic_browser_exporter.py --hours 24 --resolution 1h --monitor-analysis

# 週次詳細レポート
python3 synthetic_browser_exporter.py --hours 168 --resolution 30m --monitor-analysis
```

### 問題調査
```bash
# 高解像度データでの詳細調査
python3 synthetic_browser_exporter.py --hours 6 --resolution 5m --monitor-analysis
```

### 特定環境監視
```bash
# 本番環境のみ（監視別分析付き）
python3 synthetic_browser_exporter.py --tag Environment:Production --monitor-analysis

# 特定チーム担当監視のみ
python3 synthetic_browser_exporter.py --tag Owner:TeamName --monitor-analysis
```

---

## メトリクス詳細リファレンス

### 取得可能メトリクス詳細一覧（最大67種類）

**重要**: 以下は取得を試行する全メトリクス一覧です。実際のCSV出力には、データが存在するメトリクスのみが含まれます。

#### 出力条件
- **標準実行**: 最大67種類のメトリクスを試行
- **地域データ除外（`--no-geo`）**: 約33種類のメトリクスを試行（.geoサフィックス除外）
- **実際のCSV**: データが存在するメトリクスのみが出力される

#### Core Web Vitals（Google推奨指標）

| メトリクス名（CSV出力名） | 説明 | 単位 | 良好 | 要改善 | 重要度 |
|------------|------|------|------|--------|--------|
| `builtin:synthetic.browser.largestContentfulPaint.load` | 最大コンテンツの描画時間（LCP） | ms | ≤2500 | >4000 | ★★★ |
| `builtin:synthetic.browser.cumulativeLayoutShift.load` | レイアウトシフトの累積スコア（CLS） | score | ≤0.1 | >0.25 | ★★★ |

#### 主要パフォーマンス指標

| メトリクス名（CSV出力名） | 説明 | 単位 | 良好 | 要改善 | 重要度 |
|------------|------|------|------|--------|--------|
| `builtin:synthetic.browser.actionDuration.load` | ページの完全ロードにかかる時間 | ms | ≤3000 | >5000 | ★★★ |
| `builtin:synthetic.browser.speedIndex.load` | ページの視覚的な読み込み速度 | ms | ≤3400 | >5800 | ★★★ |
| `builtin:synthetic.browser.visuallyComplete.load` | ビューポートの完全な描画時間 | ms | ≤4000 | >6000 | ★★☆ |
| `builtin:synthetic.browser.domInteractive.load` | DOMが操作可能になるまでの時間 | ms | ≤1500 | >3000 | ★★☆ |

#### ネットワーク・サーバー指標

| メトリクス名（CSV出力名） | 説明 | 単位 | 良好 | 要改善 | 重要度 |
|------------|------|------|------|--------|--------|
| `builtin:synthetic.browser.firstByte.load` | 最初のバイト受信時間（TTFB） | ms | ≤600 | >1000 | ★★★ |
| `builtin:synthetic.browser.responseEnd.load` | レスポンス受信完了時間 | ms | ≤800 | >1500 | ★★☆ |
| `builtin:synthetic.browser.networkContribution.load` | ネットワーク処理時間の寄与度 | ms | 参考値 | 参考値 | ★☆☆ |
| `builtin:synthetic.browser.serverContribution.load` | サーバー処理時間の寄与度 | ms | 参考値 | 参考値 | ★☆☆ |

#### ページライフサイクル指標

| メトリクス名（CSV出力名） | 説明 | 単位 | 用途 | 重要度 |
|------------|------|------|------|--------|
| `builtin:synthetic.browser.loadEventStart.load` | loadイベント開始時間 | ms | 詳細分析 | ★☆☆ |
| `builtin:synthetic.browser.loadEventEnd.load` | loadイベント完了時間 | ms | 詳細分析 | ★☆☆ |

#### 可用性・信頼性指標

| メトリクス名（CSV出力名） | 説明 | 単位 | 良好 | 要改善 | 重要度 |
|------------|------|------|------|--------|--------|
| `builtin:synthetic.browser.availability` | 監視の成功率 | % | ≥99 | <95 | ★★★ |
| `builtin:synthetic.browser.success` | 成功した監視実行数 | count | 参考値 | 参考値 | ★★☆ |
| `builtin:synthetic.browser.failure` | 失敗した監視実行数 | count | 参考値 | 参考値 | ★★☆ |
| `builtin:synthetic.browser.total` | 総監視実行数 | count | 参考値 | 参考値 | ★☆☆ |
| `builtin:synthetic.browser.totalDuration` | 総監視実行時間 | ms | 参考値 | 参考値 | ★☆☆ |

#### 地域別分析対応メトリクス

上記の主要メトリクスには `.geo` サフィックス付きの地域別データが利用可能：

| 地域別メトリクス例（CSV出力名） | 用途 | 分析観点 |
|------------------|------|---------|
| `builtin:synthetic.browser.actionDuration.load.geo` | 地域別ページロード時間 | CDN効果測定 |
| `builtin:synthetic.browser.largestContentfulPaint.load.geo` | 地域別LCP | グローバル最適化 |
| `builtin:synthetic.browser.availability.geo` | 地域別可用性 | 地域障害検知 |

#### イベント系詳細メトリクス

| メトリクス分類 | 説明 | 用途 |
|--------------|------|------|
| **Event系メトリクス** (`builtin:synthetic.browser.event.*`) | 各パフォーマンス指標のイベント単位データ | 詳細分析・異常検知 |
| **Location系メトリクス** (`builtin:synthetic.browser.availability.location.*`) | 監視地点別の可用性データ | 地点別分析 |

#### 全67種類メトリクス完全一覧

**注意**: 以下は取得を試行する全メトリクス定義です。実際のCSV出力は以下の条件で決まります：
- **データの存在**: Dynatrace環境でデータが生成されているメトリクスのみ
- **監視設定**: Browser監視の設定内容による  
- **実行オプション**: `--no-geo`指定時は.geoサフィックスのメトリクスを除外

<details>
<summary>全メトリクス一覧を表示（クリックして展開）</summary>

| No. | メトリクス名（CSV出力名） | カテゴリ | 単位 |
|-----|------------------------|---------|------|
| 1 | `builtin:synthetic.browser.actionDuration.load` | パフォーマンス | ms |
| 2 | `builtin:synthetic.browser.actionDuration.load.geo` | パフォーマンス（地域別） | ms |
| 3 | `builtin:synthetic.browser.availability` | 可用性 | % |
| 4 | `builtin:synthetic.browser.availability.location.total` | 可用性（地点別） | % |
| 5 | `builtin:synthetic.browser.availability.location.totalWoMaintenanceWindow` | 可用性（地点別・メンテ除外） | % |
| 6 | `builtin:synthetic.browser.cumulativeLayoutShift.load` | Core Web Vitals | score |
| 7 | `builtin:synthetic.browser.cumulativeLayoutShift.load.geo` | Core Web Vitals（地域別） | score |
| 8 | `builtin:synthetic.browser.domInteractive.load` | パフォーマンス | ms |
| 9 | `builtin:synthetic.browser.domInteractive.load.geo` | パフォーマンス（地域別） | ms |
| 10 | `builtin:synthetic.browser.event.actionDuration.load` | イベント系 | ms |
| 11 | `builtin:synthetic.browser.event.actionDuration.load.geo` | イベント系（地域別） | ms |
| 12 | `builtin:synthetic.browser.event.cumulativeLayoutShift.load` | イベント系 | score |
| 13 | `builtin:synthetic.browser.event.cumulativeLayoutShift.load.geo` | イベント系（地域別） | score |
| 14 | `builtin:synthetic.browser.event.domInteractive.load` | イベント系 | ms |
| 15 | `builtin:synthetic.browser.event.domInteractive.load.geo` | イベント系（地域別） | ms |
| 16 | `builtin:synthetic.browser.event.failure` | イベント系 | count |
| 17 | `builtin:synthetic.browser.event.failure.geo` | イベント系（地域別） | count |
| 18 | `builtin:synthetic.browser.event.firstByte.load` | イベント系 | ms |
| 19 | `builtin:synthetic.browser.event.firstByte.load.geo` | イベント系（地域別） | ms |
| 20 | `builtin:synthetic.browser.event.largestContentfulPaint.load` | イベント系 | ms |
| 21 | `builtin:synthetic.browser.event.largestContentfulPaint.load.geo` | イベント系（地域別） | ms |
| 22 | `builtin:synthetic.browser.event.loadEventEnd.load` | イベント系 | ms |
| 23 | `builtin:synthetic.browser.event.loadEventEnd.load.geo` | イベント系（地域別） | ms |
| 24 | `builtin:synthetic.browser.event.loadEventStart.load` | イベント系 | ms |
| 25 | `builtin:synthetic.browser.event.loadEventStart.load.geo` | イベント系（地域別） | ms |
| 26 | `builtin:synthetic.browser.event.networkContribution.load` | イベント系 | ms |
| 27 | `builtin:synthetic.browser.event.networkContribution.load.geo` | イベント系（地域別） | ms |
| 28 | `builtin:synthetic.browser.event.responseEnd.load` | イベント系 | ms |
| 29 | `builtin:synthetic.browser.event.responseEnd.load.geo` | イベント系（地域別） | ms |
| 30 | `builtin:synthetic.browser.event.serverContribution.load` | イベント系 | ms |
| 31 | `builtin:synthetic.browser.event.serverContribution.load.geo` | イベント系（地域別） | ms |
| 32 | `builtin:synthetic.browser.event.speedIndex.load` | イベント系 | ms |
| 33 | `builtin:synthetic.browser.event.speedIndex.load.geo` | イベント系（地域別） | ms |
| 34 | `builtin:synthetic.browser.event.success` | イベント系 | count |
| 35 | `builtin:synthetic.browser.event.success.geo` | イベント系（地域別） | count |
| 36 | `builtin:synthetic.browser.event.total` | イベント系 | count |
| 37 | `builtin:synthetic.browser.event.total.geo` | イベント系（地域別） | count |
| 38 | `builtin:synthetic.browser.event.totalDuration` | イベント系 | ms |
| 39 | `builtin:synthetic.browser.event.totalDuration.geo` | イベント系（地域別） | ms |
| 40 | `builtin:synthetic.browser.event.visuallyComplete.load` | イベント系 | ms |
| 41 | `builtin:synthetic.browser.event.visuallyComplete.load.geo` | イベント系（地域別） | ms |
| 42 | `builtin:synthetic.browser.failure` | 可用性 | count |
| 43 | `builtin:synthetic.browser.failure.geo` | 可用性（地域別） | count |
| 44 | `builtin:synthetic.browser.firstByte.load` | ネットワーク | ms |
| 45 | `builtin:synthetic.browser.firstByte.load.geo` | ネットワーク（地域別） | ms |
| 46 | `builtin:synthetic.browser.largestContentfulPaint.load` | Core Web Vitals | ms |
| 47 | `builtin:synthetic.browser.largestContentfulPaint.load.geo` | Core Web Vitals（地域別） | ms |
| 48 | `builtin:synthetic.browser.loadEventEnd.load` | ページライフサイクル | ms |
| 49 | `builtin:synthetic.browser.loadEventEnd.load.geo` | ページライフサイクル（地域別） | ms |
| 50 | `builtin:synthetic.browser.loadEventStart.load` | ページライフサイクル | ms |
| 51 | `builtin:synthetic.browser.loadEventStart.load.geo` | ページライフサイクル（地域別） | ms |
| 52 | `builtin:synthetic.browser.networkContribution.load` | ネットワーク | ms |
| 53 | `builtin:synthetic.browser.networkContribution.load.geo` | ネットワーク（地域別） | ms |
| 54 | `builtin:synthetic.browser.responseEnd.load` | ネットワーク | ms |
| 55 | `builtin:synthetic.browser.responseEnd.load.geo` | ネットワーク（地域別） | ms |
| 56 | `builtin:synthetic.browser.serverContribution.load` | サーバー | ms |
| 57 | `builtin:synthetic.browser.serverContribution.load.geo` | サーバー（地域別） | ms |
| 58 | `builtin:synthetic.browser.speedIndex.load` | パフォーマンス | ms |
| 59 | `builtin:synthetic.browser.speedIndex.load.geo` | パフォーマンス（地域別） | ms |
| 60 | `builtin:synthetic.browser.success` | 可用性 | count |
| 61 | `builtin:synthetic.browser.success.geo` | 可用性（地域別） | count |
| 62 | `builtin:synthetic.browser.total` | 可用性 | count |
| 63 | `builtin:synthetic.browser.total.geo` | 可用性（地域別） | count |
| 64 | `builtin:synthetic.browser.totalDuration` | 可用性 | ms |
| 65 | `builtin:synthetic.browser.totalDuration.geo` | 可用性（地域別） | ms |
| 66 | `builtin:synthetic.browser.visuallyComplete.load` | パフォーマンス | ms |
| 67 | `builtin:synthetic.browser.visuallyComplete.load.geo` | パフォーマンス（地域別） | ms |

</details>

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

本ツールにより、Dynatrace Synthetic Browser監視の最大67種類のメトリクスを効率的にExcel分析可能な形式で取得できます。特に`--monitor-analysis`オプションを使用することで、監視別にグルーピングされた最も使いやすいCSVファイルを生成できます。

定期的な性能監視、詳細な問題分析、包括的なレポート作成に活用してください。基本的な実行方法を習得後、業務要件に応じてオプションパラメータを活用し、効果的なWebサイト性能分析を実施してください。 