# Dynatrace Synthetic Browser監視データエクスポーター
**完全ガイド：環境構築から実行まで**  
作成日: 2025-01-26  
バージョン: 2.0

## このツールについて

このツールは、Dynatrace のSynthetic Browser監視データを簡単にExcelで分析できるCSVファイルにエクスポートするツールです。  
**67種類のパフォーマンスメトリクス**を自動収集し、Web サイトの性能分析レポートを生成します。

### こんな方におすすめ
- Webサイトのパフォーマンスを定期的に分析したい
- Dynatrace のデータをExcelで詳しく分析したい
- 複数の監視結果を一度にまとめて確認したい
- 技術的な詳細は分からないが、分析結果だけ欲しい

### 対応OS
- **macOS**: macOS 10.14以上
- **Windows**: Windows 10以上 
- **Linux**: Ubuntu 18.04以上（上級者向け）

### 取得できるデータ
- **Core Web Vitals**: LCP、CLS（Googleの推奨指標）
- **ページパフォーマンス**: ロード時間、Speed Index、表示完了時間
- **ネットワーク分析**: TTFB、レスポンス時間、サーバー負荷
- **可用性データ**: 成功率、失敗率、地域別データ

---

## **STEP 1: 環境構築（初回のみ）**

### 1-1. 必要なソフトウェアの確認

#### Python の確認

**macOS の場合:**
1. **Finderを開く** → **アプリケーション** → **ユーティリティ** → **ターミナル**をダブルクリック
2. 以下のコマンドを入力してEnterキーを押す：
   ```bash
   python3 --version
   ```

**Windows の場合:**
1. **スタートメニュー** → **「cmd」と入力** → **コマンドプロンプト**をクリック
2. 以下のコマンドを入力してEnterキーを押す：
   ```cmd
   python --version
   ```
   または
   ```cmd
   py --version
   ```

**成功条件:**
`Python 3.x.x` と表示されればOK（3.8以上推奨）

**エラーが出た場合:**
- [Python公式サイト](https://www.python.org/downloads/)からPython 3をダウンロード・インストール
- インストール後、コマンドプロンプト/ターミナルを再起動して再度確認

#### ファイルのダウンロード確認
1. このプロジェクトフォルダが完全にダウンロードされていることを確認
2. 以下のファイルが揃っていることを確認：
   - `README.md`（このファイル）
   - `synthetic_browser_exporter.py`
   - `requirements.txt`
   - `run_synthetic_exporter.sh`
   - `.env.template`

### 1-2. プロジェクトフォルダに移動

**macOS の場合:**
1. **ターミナル**で、プロジェクトフォルダに移動：
   ```bash
   cd ~/Downloads/dt-synthetic-exporter
   ```
   **ヒント**: フォルダをターミナルにドラッグ&ドロップすると自動でパスが入力されます

2. 正しいフォルダにいるかチェック：
   ```bash
   ls -la
   ```

**Windows の場合:**
1. **コマンドプロンプト**で、プロジェクトフォルダに移動：
   ```cmd
   cd %USERPROFILE%\Downloads\dt-synthetic-exporter
   ```
   または
   ```cmd
   cd C:\Users\あなたのユーザー名\Downloads\dt-synthetic-exporter
   ```

2. 正しいフォルダにいるかチェック：
   ```cmd
   dir
   ```

**成功条件:**
上記で確認したファイルが表示されればOK

### 1-3. Pythonライブラリのインストール

**macOS の場合:**
```bash
# 必要なライブラリを一括インストール
pip3 install -r requirements.txt

# インストール成功の確認
python3 -c "import requests, pandas; print('ライブラリインストール成功')"
```

**Windows の場合:**
```cmd
# 必要なライブラリを一括インストール
pip install -r requirements.txt

# インストール成功の確認
python -c "import requests, pandas; print('ライブラリインストール成功')"
```

**エラーが出た場合:**

**macOS:**
```bash
pip3 install requests>=2.28.0
pip3 install python-dotenv>=0.19.0
pip3 install pytz>=2021.3
pip3 install pandas
```

**Windows:**
```cmd
pip install requests>=2.28.0
pip install python-dotenv>=0.19.0
pip install pytz>=2021.3
pip install pandas
```

### 1-4. Dynatrace API設定

#### API トークンの取得
1. **Dynatrace環境**にログイン
2. **Settings** → **Integration** → **Dynatrace API** → **API tokens**
3. **Generate token**をクリック
4. **Token name**: `SyntheticExporter` などの分かりやすい名前
5. **必要な権限**にチェック：
   - `Read synthetic monitors`
   - `Read metrics`
   - `Read entities`
6. **Generate**をクリックし、トークンをコピー（**必ず保存してください**）

#### 環境設定ファイル作成

**macOS の場合:**
```bash
# 設定ファイルをコピー
cp .env.template .env

# 設定ファイルを編集
open .env
```

**Windows の場合:**
```cmd
# 設定ファイルをコピー
copy .env.template .env

# 設定ファイルを編集
notepad .env
```

**両OS共通の編集内容:**
テキストエディタが開いたら、以下のように編集：
```
DT_API_TOKEN=dt0c01.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DT_ENV_URL=https://あなたのテナント.dynatrace.com
```

**注意事項**:
- `DT_API_TOKEN=` の後に取得したAPIトークンを貼り付け
- `DT_ENV_URL=` の後にDynatraceテナントのURLを入力
- **スペースは入れない**
- **クォートは不要**

**保存方法:**
- **macOS**: Command+S で保存し、テキストエディットを閉じる
- **Windows**: Ctrl+S で保存し、メモ帳を閉じる

#### 設定確認
```bash
python3 -c "
import os
from pathlib import Path
env_file = Path('.env')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                if key == 'DT_API_TOKEN':
                    print(f'APIトークン: {value[:20]}...')
                elif key == 'DT_ENV_URL':
                    print(f'環境URL: {value}')
else:
    print('.envファイルが見つかりません')
"
```

---

## **STEP 2: 基本的な使い方**

### 2-1. 最も簡単な実行方法

**macOS の場合:**
```bash
# シンプル実行（過去72時間のデータを全て取得）
./run_synthetic_exporter.sh
```

**初回実行時**: 実行権限のエラーが出た場合：
```bash
chmod +x run_synthetic_exporter.sh
./run_synthetic_exporter.sh
```

**Windows の場合:**
```cmd
# 簡単実行（バッチファイル使用）
run_synthetic_exporter.bat
```

または

```cmd
# Pythonで直接実行
python synthetic_browser_exporter.py
```

**Windows補足**: 
- `run_synthetic_exporter.bat` はWindows用の簡単実行ファイルです
- macOSの `.sh` ファイルと同等の機能を提供します

### 2-2. 実行結果の確認

成功すると以下のファイルが `output/` フォルダに生成されます：

#### **メインファイル**
- **`ultimate_browser_results_YYYYMMDD_HHMMSS.csv`**
  - 全データの詳細
  - **Excel で開いて分析可能**

#### **サマリーファイル**
- **`ultimate_browser_results_YYYYMMDD_HHMMSS_summary.json`**  
  - 統計サマリー
  - パフォーマンス評価結果

#### **ログファイル**
- **`.logs/ultimate_browser_export_*.log`**
  - 実行ログ（エラー時の確認用）

### 2-3. 結果ファイルの開き方

**macOS の場合:**
```bash
# CSVファイルをExcelで開く
open output/ultimate_browser_results_*.csv

# サマリーをテキストエディットで確認
open output/ultimate_browser_results_*_summary.json
```

**Windows の場合:**
```cmd
# CSVファイルをExcelで開く
start output\ultimate_browser_results_*.csv

# サマリーをメモ帳で確認
start notepad output\ultimate_browser_results_*_summary.json
```

**両OS共通**: エクスプローラー/Finderで `output` フォルダを開いて、ファイルをダブルクリックでも開けます

---

## **STEP 3: カスタム実行（応用編）**

### 3-1. よく使うオプション組み合わせ

#### **特定タグの監視のみ取得**
**macOS:**
```bash
python3 synthetic_browser_exporter.py --tag Owner:Koizumi
```
**Windows:**
```cmd
python synthetic_browser_exporter.py --tag Owner:Koizumi
```

#### **期間を指定（過去48時間）**
**macOS:**
```bash
python3 synthetic_browser_exporter.py --hours 48
```
**Windows:**
```cmd
python synthetic_browser_exporter.py --hours 48
```

#### **高解像度データ（15分間隔）**
**macOS:**
```bash
python3 synthetic_browser_exporter.py --resolution 15m
```
**Windows:**
```cmd
python synthetic_browser_exporter.py --resolution 15m
```

#### **軽量化実行（地域データ除外）**
**macOS:**
```bash
python3 synthetic_browser_exporter.py --no-geo
```
**Windows:**
```cmd
python synthetic_browser_exporter.py --no-geo
```

#### **監視別詳細分析付き**
**macOS:**
```bash
python3 synthetic_browser_exporter.py --monitor-analysis
```
**Windows:**
```cmd
python synthetic_browser_exporter.py --monitor-analysis
```

### 3-2. 複合オプション例

#### **日次レポート作成**
```bash
python3 synthetic_browser_exporter.py \
  --hours 24 \
  --resolution 1h \
  --output daily_report_$(date +%Y%m%d) \
  --monitor-analysis
```

#### **特定環境の週次詳細分析**
```bash
python3 synthetic_browser_exporter.py \
  --tag Environment:Production \
  --hours 168 \
  --resolution 30m \
  --output weekly_prod_analysis \
  --monitor-analysis
```

### 3-3. オプション一覧表

| オプション | 説明 | 例 | 初心者おすすめ度 |
|-----------|------|-----|----------------|
| `--tag` | 特定タグのみ取得 | `--tag Owner:Koizumi` | おすすめ |
| `--hours` | 取得期間指定 | `--hours 48` | おすすめ |
| `--resolution` | データ間隔 | `--resolution 30m` | 中級者 |
| `--output` | ファイル名指定 | `--output my_analysis` | おすすめ |
| `--no-geo` | 地域データ除外（高速化） | `--no-geo` | 中級者 |
| `--monitor-analysis` | 監視別詳細分析 | `--monitor-analysis` | 上級者 |

---

## **STEP 4: データの見方・分析方法**

### 4-1. CSVファイルの主要カラム説明

| カラム名 | 意味 | 使い方 |
|---------|------|-------|
| `timestamp` | 測定日時 | グラフのX軸に使用 |
| `monitor_name` | 監視の名前 | 監視別にフィルタリング |
| `monitor_url` | 監視対象URL | どのサイトのデータか確認 |
| `metric_display_name` | メトリクス名（日本語） | 何の指標かを確認 |
| `value` | 測定値 | 分析の基本データ |
| `unit` | 単位 | ms（ミリ秒）、%（パーセント）など |
| `performance_status` | 評価 | Good/Warning/Critical |

### 4-2. パフォーマンス評価基準

#### **Good（良好）**
- **LCP（最大コンテンツ描画）**: 2.5秒以下
- **CLS（レイアウトシフト）**: 0.1以下
- **ページロード時間**: 3.0秒以下
- **可用性**: 99%以上

#### **Warning（注意）**
- **LCP**: 2.5〜4.0秒
- **CLS**: 0.1〜0.25
- **ページロード時間**: 3.0〜5.0秒
- **可用性**: 95〜99%

#### **Critical（要改善）**
- **LCP**: 4.0秒超
- **CLS**: 0.25超
- **ページロード時間**: 5.0秒超
- **可用性**: 95%未満

### 4-3. Excelでの分析手順

#### **基本分析**
1. **CSVをExcelで開く**
2. **データタブ** → **テーブルとして書式設定**
3. **フィルター機能**を使って分析：
   - `monitor_name` で特定の監視をフィルタ
   - `performance_status` で問題のあるデータを確認
   - `metric_display_name` で特定指標を抽出

#### **グラフ作成**
1. **時系列グラフ**:
   - X軸: `timestamp`
   - Y軸: `value`
   - 系列: `metric_display_name`

2. **監視比較グラフ**:
   - X軸: `monitor_name`
   - Y軸: `value` の平均
   - 系列: `metric_display_name`

---

## **トラブルシューティング**

### よくあるエラーと解決方法

#### **「環境変数が設定されていません」**
```bash
# .envファイルの確認
cat .env

# 正しく設定されているかチェック
python3 -c "
import os
from pathlib import Path
env_file = Path('.env')
if env_file.exists():
    print('.envファイル存在')
    with open(env_file) as f:
        content = f.read()
        if 'DT_API_TOKEN=' in content and 'DT_ENV_URL=' in content:
            print('設定項目確認')
        else:
            print('設定項目不足')
else:
    print('.envファイル不存在')
"
```

**解決方法**: STEP 1-4 を再実行

#### **「データが取得できませんでした」**

**原因チェック**:
```bash
python3 -c "
import os
from pathlib import Path
# .env読み込み
env_file = Path('.env')
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

import requests
api_token = os.getenv('DT_API_TOKEN')
env_url = os.getenv('DT_ENV_URL')
try:
    response = requests.get(f'{env_url}/api/v1/synthetic/monitors', 
                           headers={'Authorization': f'Api-Token {api_token}'})
    if response.status_code == 200:
        monitors = response.json().get('monitors', [])
        browser_monitors = [m for m in monitors if m.get('type') == 'BROWSER']
        print(f'接続成功: Browser監視数 {len(browser_monitors)}')
        for m in browser_monitors[:3]:  # 最初の3件表示
            print(f'  - {m[\"name\"]}')
    else:
        print(f'API接続エラー: {response.status_code}')
        print(f'レスポンス: {response.text[:200]}')
except Exception as e:
    print(f'接続エラー: {e}')
"
```

**解決方法**:
1. APIトークンの権限を再確認
2. DynatraceテナントURLが正しいか確認
3. ネットワーク接続を確認

#### **「ライブラリがインストールできない」**
```bash
# pip のアップグレード
pip3 install --upgrade pip

# 個別インストール試行
pip3 install requests
pip3 install pandas
pip3 install python-dotenv
pip3 install pytz
```

#### **「メモリ不足」**
```bash
# 軽量化オプションで実行
python3 synthetic_browser_exporter.py --no-geo --hours 12 --resolution 4h
```

#### **「Permission denied」（権限エラー）**
```bash
# 実行権限付与
chmod +x run_synthetic_exporter.sh

# または直接Python実行
python3 synthetic_browser_exporter.py
```

---

## **日常的な使い方（推奨パターン）**

### **毎日の定期チェック**
```bash
# 毎朝実行して前日のパフォーマンスをチェック
python3 synthetic_browser_exporter.py \
  --hours 24 \
  --resolution 1h \
  --output daily_$(date +%Y%m%d)
```

### **週次レポート作成**
```bash
# 毎週月曜日に過去1週間の詳細分析
python3 synthetic_browser_exporter.py \
  --hours 168 \
  --resolution 30m \
  --output weekly_$(date +%Y%m%d) \
  --monitor-analysis
```

### **問題調査時**
```bash
# 特定期間の高解像度データ取得
python3 synthetic_browser_exporter.py \
  --hours 6 \
  --resolution 5m \
  --output incident_analysis_$(date +%Y%m%d_%H%M)
```

### **特定監視のみチェック**
```bash
# 本番環境のみ
python3 synthetic_browser_exporter.py --tag Environment:Production

# 特定オーナーのみ
python3 synthetic_browser_exporter.py --tag Owner:あなたの名前
```

---

## **サポート・問い合わせ**

### **問い合わせ前のチェックリスト**
1. 最新のログファイル（`.logs/`フォルダ内）を確認
2. `.env` ファイルの設定を再確認
3. Dynatrace環境への接続を確認
4. Python とライブラリのバージョンを確認

### **ログファイルの場所**
```bash
# 最新のログを確認
ls -la .logs/
tail -20 .logs/ultimate_browser_export_*.log
```

### **デバッグ実行**
詳細なエラー情報が必要な場合：
```bash
python3 synthetic_browser_exporter.py --hours 1 2>&1 | tee debug_output.txt
```

---

## **まとめ**

このツールを使用することで、Dynatrace Synthetic Browser監視の**67種類のメトリクス**を簡単にExcel分析できるCSVファイルとしてエクスポートできます。

### **覚えておくべき基本コマンド**
```bash
# 最も基本的な実行
./run_synthetic_exporter.sh

# 特定タグのみ（最も使用頻度が高い）
python3 synthetic_browser_exporter.py --tag Owner:あなたの名前

# 期間指定（2番目に使用頻度が高い）
python3 synthetic_browser_exporter.py --hours 48
```

### **活用のコツ**
1. **定期実行**: 毎日/毎週決まった時間に実行
2. **タグ活用**: 自分担当の監視のみフィルタリング
3. **Excel分析**: フィルター機能とグラフ機能をフル活用
4. **トレンド分析**: 時系列データで傾向を把握

**これで完璧にSynthetic監視データ分析ができます！** 