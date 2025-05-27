#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終版Browser監視結果エクスポーター v2 (修正版)
作成日: 2025-01-26

67個の動作確認済みメトリクス + データ構造修正対応
"""

import os
import json
import logging
import requests
import pandas as pd
import argparse
import pytz
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


def setup_logging():
    """ログ設定"""
    log_dir = Path('.logs')
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'ultimate_browser_export_v2_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class UltimateBrowserExporterV2:
    """最終版Browser監視結果エクスポーター v2"""
    
    # 動作確認済み67個のメトリクス
    WORKING_METRICS = [
        'builtin:synthetic.browser.actionDuration.load',
        'builtin:synthetic.browser.actionDuration.load.geo',
        'builtin:synthetic.browser.availability',
        'builtin:synthetic.browser.availability.location.total',
        'builtin:synthetic.browser.availability.location.totalWoMaintenanceWindow',
        'builtin:synthetic.browser.cumulativeLayoutShift.load',
        'builtin:synthetic.browser.cumulativeLayoutShift.load.geo',
        'builtin:synthetic.browser.domInteractive.load',
        'builtin:synthetic.browser.domInteractive.load.geo',
        'builtin:synthetic.browser.event.actionDuration.load',
        'builtin:synthetic.browser.event.actionDuration.load.geo',
        'builtin:synthetic.browser.event.cumulativeLayoutShift.load',
        'builtin:synthetic.browser.event.cumulativeLayoutShift.load.geo',
        'builtin:synthetic.browser.event.domInteractive.load',
        'builtin:synthetic.browser.event.domInteractive.load.geo',
        'builtin:synthetic.browser.event.failure',
        'builtin:synthetic.browser.event.failure.geo',
        'builtin:synthetic.browser.event.firstByte.load',
        'builtin:synthetic.browser.event.firstByte.load.geo',
        'builtin:synthetic.browser.event.largestContentfulPaint.load',
        'builtin:synthetic.browser.event.largestContentfulPaint.load.geo',
        'builtin:synthetic.browser.event.loadEventEnd.load',
        'builtin:synthetic.browser.event.loadEventEnd.load.geo',
        'builtin:synthetic.browser.event.loadEventStart.load',
        'builtin:synthetic.browser.event.loadEventStart.load.geo',
        'builtin:synthetic.browser.event.networkContribution.load',
        'builtin:synthetic.browser.event.networkContribution.load.geo',
        'builtin:synthetic.browser.event.responseEnd.load',
        'builtin:synthetic.browser.event.responseEnd.load.geo',
        'builtin:synthetic.browser.event.serverContribution.load',
        'builtin:synthetic.browser.event.serverContribution.load.geo',
        'builtin:synthetic.browser.event.speedIndex.load',
        'builtin:synthetic.browser.event.speedIndex.load.geo',
        'builtin:synthetic.browser.event.success',
        'builtin:synthetic.browser.event.success.geo',
        'builtin:synthetic.browser.event.total',
        'builtin:synthetic.browser.event.total.geo',
        'builtin:synthetic.browser.event.totalDuration',
        'builtin:synthetic.browser.event.totalDuration.geo',
        'builtin:synthetic.browser.event.visuallyComplete.load',
        'builtin:synthetic.browser.event.visuallyComplete.load.geo',
        'builtin:synthetic.browser.failure',
        'builtin:synthetic.browser.failure.geo',
        'builtin:synthetic.browser.firstByte.load',
        'builtin:synthetic.browser.firstByte.load.geo',
        'builtin:synthetic.browser.largestContentfulPaint.load',
        'builtin:synthetic.browser.largestContentfulPaint.load.geo',
        'builtin:synthetic.browser.loadEventEnd.load',
        'builtin:synthetic.browser.loadEventEnd.load.geo',
        'builtin:synthetic.browser.loadEventStart.load',
        'builtin:synthetic.browser.loadEventStart.load.geo',
        'builtin:synthetic.browser.networkContribution.load',
        'builtin:synthetic.browser.networkContribution.load.geo',
        'builtin:synthetic.browser.responseEnd.load',
        'builtin:synthetic.browser.responseEnd.load.geo',
        'builtin:synthetic.browser.serverContribution.load',
        'builtin:synthetic.browser.serverContribution.load.geo',
        'builtin:synthetic.browser.speedIndex.load',
        'builtin:synthetic.browser.speedIndex.load.geo',
        'builtin:synthetic.browser.success',
        'builtin:synthetic.browser.success.geo',
        'builtin:synthetic.browser.total',
        'builtin:synthetic.browser.total.geo',
        'builtin:synthetic.browser.totalDuration',
        'builtin:synthetic.browser.totalDuration.geo',
        'builtin:synthetic.browser.visuallyComplete.load',
        'builtin:synthetic.browser.visuallyComplete.load.geo'
    ]
    
    # メトリクス詳細情報（Web Vitals準拠）
    METRIC_INFO = {
        # Core Web Vitals
        'builtin:synthetic.browser.largestContentfulPaint.load': {
            'display_name': 'Largest Contentful Paint (LCP)',
            'description': '最大コンテンツの描画時間',
            'unit': 'ms',
            'category': 'Core Web Vitals',
            'good_threshold': 2500,
            'warning_threshold': 4000
        },
        'builtin:synthetic.browser.cumulativeLayoutShift.load': {
            'display_name': 'Cumulative Layout Shift (CLS)',
            'description': 'レイアウトシフトの累積スコア',
            'unit': 'score',
            'category': 'Core Web Vitals',
            'good_threshold': 0.1,
            'warning_threshold': 0.25
        },
        
        # Performance Metrics
        'builtin:synthetic.browser.actionDuration.load': {
            'display_name': 'ページロード時間',
            'description': 'ページの完全ロードにかかる時間',
            'unit': 'ms',
            'category': 'パフォーマンス',
            'good_threshold': 3000,
            'warning_threshold': 5000
        },
        'builtin:synthetic.browser.speedIndex.load': {
            'display_name': 'Speed Index',
            'description': 'ページの視覚的な読み込み速度',
            'unit': 'ms',
            'category': 'パフォーマンス',
            'good_threshold': 3400,
            'warning_threshold': 5800
        },
        'builtin:synthetic.browser.visuallyComplete.load': {
            'display_name': 'Visually Complete',
            'description': 'ビューポートの完全な描画時間',
            'unit': 'ms',
            'category': 'パフォーマンス',
            'good_threshold': 4000,
            'warning_threshold': 6000
        },
        'builtin:synthetic.browser.firstByte.load': {
            'display_name': 'Time to First Byte (TTFB)',
            'description': '最初のバイト受信時間',
            'unit': 'ms',
            'category': 'ネットワーク',
            'good_threshold': 800,
            'warning_threshold': 1800
        },
        'builtin:synthetic.browser.domInteractive.load': {
            'display_name': 'DOM Interactive',
            'description': 'DOMが操作可能になるまでの時間',
            'unit': 'ms',
            'category': 'パフォーマンス',
            'good_threshold': 2000,
            'warning_threshold': 4000
        },
        
        # Availability
        'builtin:synthetic.browser.availability': {
            'display_name': '可用性',
            'description': '監視の成功率',
            'unit': '%',
            'category': '可用性',
            'good_threshold': 99.0,
            'warning_threshold': 95.0
        }
    }
    
    def __init__(self, api_token: str, env_url: str):
        """初期化"""
        self.api_token = api_token
        self.env_url = env_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Api-Token {api_token}',
            'Content-Type': 'application/json'
        })
        self.logger = logging.getLogger(__name__)
    
    def load_env_from_file(self):
        """環境変数を.envファイルから読み込み"""
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    def get_browser_monitors(self, tags: Optional[List[str]] = None) -> List[Dict]:
        """Browser監視一覧を取得"""
        url = f"{self.env_url}/api/v1/synthetic/monitors"
        params = {}
        
        if tags:
            params['tag'] = tags
        
        self.logger.info(f"Browser監視一覧取得中... フィルタ: {params}")
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            monitors = response.json().get('monitors', [])
            # Browser監視のみフィルタ
            browser_monitors = [m for m in monitors if m.get('type') == 'BROWSER']
            
            self.logger.info(f"取得したBrowser監視数: {len(browser_monitors)}")
            return browser_monitors
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"監視一覧取得エラー: {e}")
            return []
    
    def get_monitor_details(self, monitor_id: str) -> Optional[Dict]:
        """監視の詳細情報を取得"""
        url = f"{self.env_url}/api/v1/synthetic/monitors/{monitor_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"監視詳細取得エラー ({monitor_id}): {e}")
            return None
    
    def get_metrics_data(self, 
                        metric_selector: str,
                        entity_selector: str,
                        from_time: str,
                        to_time: str,
                        resolution: str = "1h") -> Optional[Dict]:
        """メトリクスデータを取得"""
        url = f"{self.env_url}/api/v2/metrics/query"
        
        params = {
            'metricSelector': metric_selector,
            'entitySelector': entity_selector,
            'from': from_time,
            'to': to_time,
            'resolution': resolution
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"メトリクス取得エラー ({metric_selector}): {e}")
            return None
    
    def collect_comprehensive_data(self,
                                 tags: Optional[List[str]] = None,
                                 hours: int = 24,
                                 resolution: str = "1h",
                                 include_geo: bool = True) -> pd.DataFrame:
        """包括的データ収集"""
        
        # 時間範囲設定（JST基準、より正確な24時間）
        import pytz
        jst = pytz.timezone('Asia/Tokyo')
        
        # 現在のJST時刻を取得
        now_jst = datetime.now(jst)
        from_jst = now_jst - timedelta(hours=hours)
        
        # 解像度に応じて時刻を調整（データポイントの境界に合わせる）
        # raw_timeオプションが指定されていない場合のみ調整
        if not getattr(self, 'raw_time', False):
            if resolution == "5m":
                # 5分単位に調整
                from_jst = from_jst.replace(minute=(from_jst.minute // 5) * 5, second=0, microsecond=0)
                now_jst = now_jst.replace(minute=(now_jst.minute // 5) * 5, second=0, microsecond=0)
            elif resolution == "15m":
                # 15分単位に調整
                from_jst = from_jst.replace(minute=(from_jst.minute // 15) * 15, second=0, microsecond=0)
                now_jst = now_jst.replace(minute=(now_jst.minute // 15) * 15, second=0, microsecond=0)
            elif resolution == "1h":
                # 1時間単位に調整
                from_jst = from_jst.replace(minute=0, second=0, microsecond=0)
                now_jst = now_jst.replace(minute=0, second=0, microsecond=0)
        
        # UTCに変換してAPI用文字列作成
        to_time_utc = now_jst.astimezone(pytz.UTC)
        from_time_utc = from_jst.astimezone(pytz.UTC)
        
        from_str = from_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        to_str = to_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        self.logger.info(f"JST時刻範囲: {from_jst.strftime('%Y-%m-%d %H:%M:%S JST')} ～ {now_jst.strftime('%Y-%m-%d %H:%M:%S JST')}")
        self.logger.info(f"API送信時刻範囲: {from_str} ～ {to_str}")
        self.logger.info(f"データ解像度: {resolution}")
        
        # Browser監視一覧取得
        monitors = self.get_browser_monitors(tags)
        if not monitors:
            self.logger.warning("Browser監視が見つかりませんでした")
            return pd.DataFrame()
        
        # 使用するメトリクス選択
        metrics_to_use = self.WORKING_METRICS
        if not include_geo:
            # .geoサフィックスのメトリクスを除外
            metrics_to_use = [m for m in self.WORKING_METRICS if not m.endswith('.geo')]
        
        self.logger.info(f"使用メトリクス数: {len(metrics_to_use)}")
        
        all_data = []
        
        for monitor in monitors:
            monitor_id = monitor['entityId']
            monitor_name = monitor['name']
            monitor_type = monitor.get('type', 'BROWSER')
            monitor_url = monitor.get('script', {}).get('configuration', {}).get('url', 'N/A')
            
            self.logger.info(f"処理中: {monitor_name} ({monitor_id})")
            
            # 監視詳細取得
            details = self.get_monitor_details(monitor_id)
            
            # タグ情報取得
            tags_dict = {}
            if details and 'tags' in details:
                for tag in details['tags']:
                    if isinstance(tag, dict) and 'key' in tag and 'value' in tag:
                        tags_dict[tag['key']] = tag['value']
            
            # 監視設定情報
            monitor_info = {
                'frequency': details.get('frequencyMin', 'N/A') if details else 'N/A',
                'locations': len(details.get('locations', [])) if details else 0,
                'enabled': details.get('enabled', False) if details else False
            }
            
            # 各メトリクスのデータ取得
            for metric in metrics_to_use:
                self.logger.debug(f"  メトリクス取得: {metric}")
                
                entity_selector = f'type(SYNTHETIC_TEST),entityId("{monitor_id}")'
                metrics_data = self.get_metrics_data(
                    metric, entity_selector, from_str, to_str, resolution
                )
                
                if metrics_data and 'result' in metrics_data:
                    for result in metrics_data['result']:
                        metric_id = result.get('metricId', metric)
                        
                        # 新しいデータ構造に対応
                        if 'data' in result:
                            # v5構造（data配列）
                            for data_item in result['data']:
                                if 'timestamps' in data_item and 'values' in data_item:
                                    timestamps = data_item['timestamps']
                                    values = data_item['values']
                                    dimension_map = data_item.get('dimensionMap', {})
                                    
                                    # timestampsとvaluesの長さが一致することを確認
                                    if len(timestamps) == len(values):
                                        for timestamp, value in zip(timestamps, values):
                                            # Noneでない値のみを処理
                                            if value is not None:
                                                all_data.append(self._create_record(
                                                    timestamp, value, metric_id, monitor_id, monitor_name,
                                                    monitor_type, monitor_url, monitor_info, tags_dict,
                                                    dimension_map, resolution
                                                ))
                        
                        # 旧構造にも対応（後方互換性）
                        elif 'timestamps' in result and 'values' in result:
                            # v4構造（timestamps/values）
                            timestamps = result['timestamps']
                            values = result['values']
                            dimension_map = result.get('dimensionMap', {})
                            
                            # timestampsとvaluesの長さが一致することを確認
                            if len(timestamps) == len(values):
                                for timestamp, value in zip(timestamps, values):
                                    # Noneでない値のみを処理
                                    if value is not None:
                                        all_data.append(self._create_record(
                                            timestamp, value, metric_id, monitor_id, monitor_name,
                                            monitor_type, monitor_url, monitor_info, tags_dict,
                                            dimension_map, resolution
                                        ))
        
        if all_data:
            df = pd.DataFrame(all_data)
            self.logger.info(f"収集完了: {len(df)} レコード")
            return df
        else:
            self.logger.warning("データが取得できませんでした")
            return pd.DataFrame()
    
    def _create_record(self, timestamp, value, metric_id, monitor_id, monitor_name,
                      monitor_type, monitor_url, monitor_info, tags_dict,
                      dimension_map, resolution) -> Dict:
        """データレコードを作成"""
        # メトリクス詳細情報
        metric_info = self.METRIC_INFO.get(metric_id, {
            'display_name': metric_id.split('.')[-1],
            'description': metric_id,
            'unit': 'unknown',
            'category': 'その他'
        })
        
        # パフォーマンス評価
        performance_status = self._evaluate_performance(
            metric_id, value, metric_info
        )
        
        # データポイントを記録（タイムスタンプをJSTに変換）
        jst = pytz.timezone('Asia/Tokyo')
        utc_timestamp = pd.to_datetime(timestamp, unit='ms', utc=True)
        jst_timestamp = utc_timestamp.tz_convert(jst)
        
        record = {
            'timestamp': jst_timestamp.strftime('%Y-%m-%d %H:%M:%S JST'),
            'monitor_id': monitor_id,
            'monitor_name': monitor_name,
            'monitor_type': monitor_type,
            'monitor_url': monitor_url,
            'monitor_frequency': monitor_info['frequency'],
            'monitor_locations': monitor_info['locations'],
            'monitor_enabled': monitor_info['enabled'],
            'metric_name': metric_id,
            'metric_display_name': metric_info.get('display_name', metric_id),
            'metric_category': metric_info.get('category', 'その他'),
            'value': value,
            'unit': metric_info.get('unit', 'unknown'),
            'performance_status': performance_status,
            'resolution': resolution
        }
        
        # ディメンション情報を追加
        for dim_key, dim_value in dimension_map.items():
            record[f'dimension_{dim_key}'] = dim_value
        
        # タグ情報を追加
        for tag_key, tag_value in tags_dict.items():
            record[f'tag_{tag_key}'] = tag_value
        
        return record
    
    def _evaluate_performance(self, metric_id: str, value: float, metric_info: Dict) -> str:
        """パフォーマンス評価"""
        good_threshold = metric_info.get('good_threshold')
        warning_threshold = metric_info.get('warning_threshold')
        
        if good_threshold is None or warning_threshold is None:
            return 'Unknown'
        
        # 可用性系は高い方が良い
        if 'availability' in metric_id:
            if value >= good_threshold:
                return 'Good'
            elif value >= warning_threshold:
                return 'Warning'
            else:
                return 'Critical'
        # CLSは低い方が良い（スコア）
        elif 'cumulativeLayoutShift' in metric_id:
            if value <= good_threshold:
                return 'Good'
            elif value <= warning_threshold:
                return 'Warning'
            else:
                return 'Critical'
        # その他のタイミング系は低い方が良い
        else:
            if value <= good_threshold:
                return 'Good'
            elif value <= warning_threshold:
                return 'Warning'
            else:
                return 'Critical'
    
    def generate_comprehensive_summary(self, df: pd.DataFrame) -> Dict:
        """包括的サマリーレポート生成"""
        if df.empty:
            return {}
        
        summary = {
            'report_generated': datetime.now().isoformat(),
            'data_period': {
                'start': str(df['timestamp'].min()),
                'end': str(df['timestamp'].max()),
                'total_records': len(df)
            },
            'monitors': {
                'total_count': df['monitor_name'].nunique(),
                'monitor_list': df['monitor_name'].unique().tolist()
            },
            'metrics': {
                'total_records': len(df),
                'unique_metrics': df['metric_name'].nunique(),
                'metrics_collected': df['metric_name'].unique().tolist()
            },
            'performance_analysis': {},
            'web_vitals_analysis': {},
            'category_analysis': {}
        }
        
        # カテゴリ別分析
        for category in df['metric_category'].unique():
            category_data = df[df['metric_category'] == category]
            summary['category_analysis'][category] = {
                'total_measurements': len(category_data),
                'unique_metrics': category_data['metric_name'].nunique(),
                'monitors_measured': category_data['monitor_name'].nunique()
            }
        
        # メトリクス別パフォーマンス分析
        for metric in df['metric_name'].unique():
            metric_data = df[df['metric_name'] == metric]
            
            performance_counts = metric_data['performance_status'].value_counts().to_dict()
            
            summary['performance_analysis'][metric] = {
                'total_measurements': len(metric_data),
                'average_value': metric_data['value'].mean(),
                'median_value': metric_data['value'].median(),
                'min_value': metric_data['value'].min(),
                'max_value': metric_data['value'].max(),
                'std_value': metric_data['value'].std(),
                'performance_distribution': performance_counts,
                'monitors_measured': metric_data['monitor_name'].nunique()
            }
        
        # Core Web Vitals特別分析
        web_vitals_metrics = [
            'builtin:synthetic.browser.largestContentfulPaint.load',
            'builtin:synthetic.browser.cumulativeLayoutShift.load'
        ]
        
        for metric in web_vitals_metrics:
            if metric in df['metric_name'].values:
                metric_data = df[df['metric_name'] == metric]
                good_count = len(metric_data[metric_data['performance_status'] == 'Good'])
                total_count = len(metric_data)
                
                summary['web_vitals_analysis'][metric] = {
                    'good_percentage': (good_count / total_count * 100) if total_count > 0 else 0,
                    'total_measurements': total_count,
                    'good_measurements': good_count
                }
        
        return summary
    
    def export_to_csv(self, df: pd.DataFrame, output_file: Optional[str] = None) -> str:
        """DataFrameをCSVファイルに出力"""
        # output/ディレクトリを作成
        os.makedirs('output', exist_ok=True)
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/ultimate_browser_results_v2_{timestamp}.csv'
        elif not output_file.startswith('output/'):
            output_file = f'output/{output_file}'
        
        df.to_csv(output_file, index=False, encoding='utf-8')
        self.logger.info(f"CSV出力完了: {output_file}")
        return output_file
    
    def export_summary_report(self, summary: Dict, output_file: Optional[str] = None) -> str:
        """サマリーレポートをJSONで出力"""
        # output/ディレクトリを作成
        os.makedirs('output', exist_ok=True)
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/ultimate_browser_summary_v2_{timestamp}.json'
        elif not output_file.startswith('output/'):
            output_file = f'output/{output_file}'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"サマリーレポート出力完了: {output_file}")
        return output_file

    def generate_monitor_analysis(self, df: pd.DataFrame) -> Dict:
        """監視対象別分析レポート生成（新機能）"""
        if df.empty:
            return {}
        
        analysis = {
            'report_generated': datetime.now().isoformat(),
            'analysis_type': 'monitor_focused',
            'data_period': {
                'start': str(df['timestamp'].min()),
                'end': str(df['timestamp'].max()),
                'total_records': len(df)
            },
            'monitor_analysis': {}
        }
        
        # 監視対象別の分析
        for monitor_name in df['monitor_name'].unique():
            monitor_data = df[df['monitor_name'] == monitor_name]
            
            monitor_analysis = {
                'monitor_info': {
                    'monitor_name': monitor_name,
                    'total_measurements': len(monitor_data),
                    'unique_metrics': monitor_data['metric_name'].nunique(),
                    'data_period': {
                        'start': str(monitor_data['timestamp'].min()),
                        'end': str(monitor_data['timestamp'].max())
                    }
                },
                'metrics_analysis': {}
            }
            
            # メトリクス別統計
            for metric_name in monitor_data['metric_name'].unique():
                metric_data = monitor_data[monitor_data['metric_name'] == metric_name]
                
                if len(metric_data) > 0:
                    monitor_analysis['metrics_analysis'][metric_name] = {
                        'total_measurements': len(metric_data),
                        'min_value': float(metric_data['value'].min()),
                        'max_value': float(metric_data['value'].max()),
                        'average_value': float(metric_data['value'].mean()),
                        'median_value': float(metric_data['value'].median()),
                        'std_value': float(metric_data['value'].std()) if len(metric_data) > 1 else 0.0,
                        'performance_distribution': metric_data['performance_status'].value_counts().to_dict()
                    }
            
            analysis['monitor_analysis'][monitor_name] = monitor_analysis
        
        return analysis

    def export_monitor_analysis_csv(self, df: pd.DataFrame, output_file: Optional[str] = None) -> str:
        """監視対象別分析をCSVで出力（新機能）"""
        if df.empty:
            self.logger.warning("データが空のため、監視対象別分析CSVを出力できません")
            return ""
        
        # output/ディレクトリを作成
        os.makedirs('output', exist_ok=True)
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/monitor_analysis_{timestamp}.csv'
        elif not output_file.startswith('output/'):
            output_file = f'output/{output_file}'
        
        # 監視対象別分析データを作成
        analysis_rows = []
        
        for monitor_name in df['monitor_name'].unique():
            monitor_data = df[df['monitor_name'] == monitor_name]
            
            for metric_name in monitor_data['metric_name'].unique():
                metric_data = monitor_data[monitor_data['metric_name'] == metric_name]
                
                if len(metric_data) > 0:
                    # メトリクス名を短縮（表示用）
                    short_metric = metric_name.replace('builtin:synthetic.browser.', '').replace('.load', '')
                    
                    # パフォーマンス分布を計算
                    perf_dist = metric_data['performance_status'].value_counts()
                    good_count = perf_dist.get('Good', 0)
                    warning_count = perf_dist.get('Warning', 0)
                    critical_count = perf_dist.get('Critical', 0)
                    unknown_count = perf_dist.get('Unknown', 0)
                    
                    # 主要なパフォーマンスグレードを決定
                    total_graded = good_count + warning_count + critical_count
                    if total_graded > 0:
                        if good_count / total_graded >= 0.8:
                            overall_grade = 'Good'
                        elif critical_count / total_graded >= 0.1:
                            overall_grade = 'Critical'
                        else:
                            overall_grade = 'Warning'
                    else:
                        overall_grade = 'Unknown'
                    
                    analysis_rows.append({
                        'Monitor': monitor_name,
                        'Metric': short_metric,
                        'Min': round(metric_data['value'].min(), 2),
                        'Max': round(metric_data['value'].max(), 2),
                        'Average': round(metric_data['value'].mean(), 2),
                        'Median': round(metric_data['value'].median(), 2),
                        'StdDev': round(metric_data['value'].std(), 2) if len(metric_data) > 1 else 0.0,
                        'Measurements': len(metric_data),
                        'Good': good_count,
                        'Warning': warning_count,
                        'Critical': critical_count,
                        'Unknown': unknown_count,
                        'Performance_Grade': overall_grade
                    })
        
        # DataFrameに変換してCSV出力
        analysis_df = pd.DataFrame(analysis_rows)
        analysis_df.to_csv(output_file, index=False, encoding='utf-8')
        
        self.logger.info(f"監視対象別分析CSV出力完了: {output_file}")
        return output_file

    def export_monitor_summary_csv(self, df: pd.DataFrame, output_file: Optional[str] = None) -> str:
        """監視対象別サマリーをCSVで出力（新機能）"""
        if df.empty:
            self.logger.warning("データが空のため、監視対象別サマリーCSVを出力できません")
            return ""
        
        # output/ディレクトリを作成
        os.makedirs('output', exist_ok=True)
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/monitor_summary_{timestamp}.csv'
        elif not output_file.startswith('output/'):
            output_file = f'output/{output_file}'
        
        # 監視対象別サマリーデータを作成
        summary_rows = []
        
        for monitor_name in df['monitor_name'].unique():
            monitor_data = df[df['monitor_name'] == monitor_name]
            
            # 主要メトリクスの取得
            load_time_data = monitor_data[monitor_data['metric_name'] == 'builtin:synthetic.browser.actionDuration.load']
            availability_data = monitor_data[monitor_data['metric_name'] == 'builtin:synthetic.browser.availability']
            lcp_data = monitor_data[monitor_data['metric_name'] == 'builtin:synthetic.browser.largestContentfulPaint.load']
            cls_data = monitor_data[monitor_data['metric_name'] == 'builtin:synthetic.browser.cumulativeLayoutShift.load']
            
            # 平均ロード時間
            avg_load_time = load_time_data['value'].mean() if len(load_time_data) > 0 else 0
            
            # 可用性
            avg_availability = availability_data['value'].mean() if len(availability_data) > 0 else 0
            
            # Web Vitals スコア計算
            web_vitals_score = 'Unknown'
            if len(lcp_data) > 0 and len(cls_data) > 0:
                lcp_good = len(lcp_data[lcp_data['performance_status'] == 'Good']) / len(lcp_data)
                cls_good = len(cls_data[cls_data['performance_status'] == 'Good']) / len(cls_data)
                avg_vitals = (lcp_good + cls_good) / 2
                
                if avg_vitals >= 0.8:
                    web_vitals_score = 'Good'
                elif avg_vitals >= 0.5:
                    web_vitals_score = 'Warning'
                else:
                    web_vitals_score = 'Critical'
            
            # 全体的なパフォーマンスグレード
            all_perf = monitor_data['performance_status'].value_counts()
            total_graded = all_perf.get('Good', 0) + all_perf.get('Warning', 0) + all_perf.get('Critical', 0)
            
            if total_graded > 0:
                good_ratio = all_perf.get('Good', 0) / total_graded
                critical_ratio = all_perf.get('Critical', 0) / total_graded
                
                if good_ratio >= 0.8:
                    overall_grade = 'A'
                elif good_ratio >= 0.6:
                    overall_grade = 'B'
                elif critical_ratio <= 0.1:
                    overall_grade = 'C'
                else:
                    overall_grade = 'D'
            else:
                overall_grade = 'Unknown'
            
            # 主要な問題の特定
            critical_metrics = monitor_data[monitor_data['performance_status'] == 'Critical']['metric_name'].unique()
            if len(critical_metrics) > 0:
                top_issue = f"Critical: {critical_metrics[0].replace('builtin:synthetic.browser.', '').replace('.load', '')}"
            else:
                warning_metrics = monitor_data[monitor_data['performance_status'] == 'Warning']['metric_name'].unique()
                if len(warning_metrics) > 0:
                    top_issue = f"Warning: {warning_metrics[0].replace('builtin:synthetic.browser.', '').replace('.load', '')}"
                else:
                    top_issue = 'None'
            
            summary_rows.append({
                'Monitor': monitor_name,
                'Total_Measurements': len(monitor_data),
                'Avg_Load_Time_ms': round(avg_load_time, 2),
                'Availability_Percent': round(avg_availability, 2),
                'Web_Vitals_Score': web_vitals_score,
                'Overall_Grade': overall_grade,
                'Top_Issue': top_issue,
                'Good_Count': all_perf.get('Good', 0),
                'Warning_Count': all_perf.get('Warning', 0),
                'Critical_Count': all_perf.get('Critical', 0)
            })
        
        # DataFrameに変換してCSV出力
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv(output_file, index=False, encoding='utf-8')
        
        self.logger.info(f"監視対象別サマリーCSV出力完了: {output_file}")
        return output_file

    def export_monitor_analysis_json(self, analysis: Dict, output_file: Optional[str] = None) -> str:
        """監視対象別分析をJSONで出力（新機能）"""
        # output/ディレクトリを作成
        os.makedirs('output', exist_ok=True)
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/monitor_analysis_{timestamp}.json'
        elif not output_file.startswith('output/'):
            output_file = f'output/{output_file}'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"監視対象別分析JSON出力完了: {output_file}")
        return output_file


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='最終版Browser監視結果エクスポーター v2 (修正版)')
    parser.add_argument('--tag', action='append', help='フィルタリング用タグ (例: Owner:Koizumi)')
    parser.add_argument('--hours', type=int, default=72, help='取得期間（時間）')
    parser.add_argument('--resolution', default='5m', help='データ解像度 (1h, 30m, 15m, 5m)')
    parser.add_argument('--output', help='出力ファイル名（拡張子なし）')
    parser.add_argument('--no-geo', action='store_true', help='地理的メトリクスを除外')
    parser.add_argument('--raw-time', action='store_true', help='時刻調整を無効化（実際の計測時刻をそのまま使用）')
    parser.add_argument('--monitor-analysis', action='store_true', help='監視対象別分析を追加出力（新機能）')
    
    args = parser.parse_args()
    
    # ログ設定
    logger = setup_logging()
    logger.info("最終版Browser監視結果エクスポーター v2 (修正版) 開始")
    
    # 環境変数読み込み
    exporter = UltimateBrowserExporterV2("", "")
    exporter.load_env_from_file()
    
    api_token = os.getenv('DT_API_TOKEN')
    env_url = os.getenv('DT_ENV_URL')
    
    if not api_token or not env_url:
        logger.error("環境変数 DT_API_TOKEN, DT_ENV_URL が設定されていません")
        return 1
    
    # エクスポーター初期化
    exporter = UltimateBrowserExporterV2(api_token, env_url)
    
    try:
        # raw_timeオプションをエクスポーターに設定
        exporter.raw_time = args.raw_time
        
        # データ収集
        logger.info(f"包括的データ収集開始: タグ={args.tag}, 期間={args.hours}時間")
        df = exporter.collect_comprehensive_data(
            tags=args.tag,
            hours=args.hours,
            resolution=args.resolution,
            include_geo=not args.no_geo
        )
        
        if df.empty:
            logger.warning("データが取得できませんでした")
            return 1
        
        # 出力
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = args.output or f'ultimate_browser_results_v2_{timestamp}'
        
        # CSV出力（既存機能）
        csv_file = exporter.export_to_csv(df, f'{base_name}.csv')
        print(f"✅ CSV出力: {csv_file}")
        
        # サマリーレポート生成・出力（既存機能）
        summary = exporter.generate_comprehensive_summary(df)
        summary_file = exporter.export_summary_report(summary, f'{base_name}_summary.json')
        print(f"✅ サマリーレポート: {summary_file}")
        
        # 監視対象別分析（新機能）
        if args.monitor_analysis:
            print(f"\n🔍 監視対象別分析を実行中...")
            
            # 監視対象別分析レポート生成
            monitor_analysis = exporter.generate_monitor_analysis(df)
            
            # JSON出力
            monitor_json_file = exporter.export_monitor_analysis_json(monitor_analysis, f'{base_name}_monitor_analysis.json')
            print(f"✅ 監視対象別分析JSON: {monitor_json_file}")
            
            # 詳細CSV出力
            monitor_csv_file = exporter.export_monitor_analysis_csv(df, f'{base_name}_monitor_analysis.csv')
            print(f"✅ 監視対象別分析CSV: {monitor_csv_file}")
            
            # サマリーCSV出力
            monitor_summary_file = exporter.export_monitor_summary_csv(df, f'{base_name}_monitor_summary.csv')
            print(f"✅ 監視対象別サマリーCSV: {monitor_summary_file}")
            
            # 監視対象別統計表示
            print(f"\n📊 監視対象別統計:")
            for monitor_name in df['monitor_name'].unique():
                monitor_data = df[df['monitor_name'] == monitor_name]
                print(f"   {monitor_name}: {len(monitor_data):,} レコード, {monitor_data['metric_name'].nunique()} メトリクス")
        else:
            print(f"\n💡 監視対象別分析を実行するには --monitor-analysis オプションを使用してください")
        
        # コンソール表示
        print(f"\n📊 最終版Browser監視結果サマリー:")
        print(f"   総レコード数: {len(df):,}")
        print(f"   監視数: {df['monitor_name'].nunique()}")
        print(f"   メトリクス数: {df['metric_name'].nunique()}")
        print(f"   期間: {df['timestamp'].min()} ～ {df['timestamp'].max()}")
        
        # カテゴリ別統計
        if 'metric_category' in df.columns:
            print(f"\n📈 カテゴリ別統計:")
            category_stats = df.groupby('metric_category').size().sort_values(ascending=False)
            for category, count in category_stats.items():
                print(f"   {category}: {count:,} レコード")
        
        # パフォーマンス状況
        if 'performance_status' in df.columns:
            perf_counts = df['performance_status'].value_counts()
            print(f"\n📈 パフォーマンス状況:")
            for status, count in perf_counts.items():
                print(f"   {status}: {count:,} レコード")
        
        logger.info("処理完了")
        return 0
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 