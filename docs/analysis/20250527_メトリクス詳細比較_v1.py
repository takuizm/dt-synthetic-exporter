#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メトリクス詳細比較分析 v1
作成日: 2025-05-27

公式ドキュメントのメトリクスと実際の取得結果を詳細比較
"""

# 公式ドキュメントから抽出したBrowser監視メトリクス（全リスト）
OFFICIAL_BROWSER_METRICS = [
    'builtin:synthetic.browser.actionDuration.custom',
    'builtin:synthetic.browser.actionDuration.custom.geo',
    'builtin:synthetic.browser.actionDuration.load',
    'builtin:synthetic.browser.actionDuration.load.geo',
    'builtin:synthetic.browser.actionDuration.xhr',
    'builtin:synthetic.browser.actionDuration.xhr.geo',
    'builtin:synthetic.browser.availability',
    'builtin:synthetic.browser.availability.location.total',
    'builtin:synthetic.browser.availability.location.totalWoMaintenanceWindow',
    'builtin:synthetic.browser.cumulativeLayoutShift.load',
    'builtin:synthetic.browser.cumulativeLayoutShift.load.geo',
    'builtin:synthetic.browser.domInteractive.load',
    'builtin:synthetic.browser.domInteractive.load.geo',
    'builtin:synthetic.browser.errorCodes',
    'builtin:synthetic.browser.errorCodes.geo',
    'builtin:synthetic.browser.event.actionDuration.custom',
    'builtin:synthetic.browser.event.actionDuration.custom.geo',
    'builtin:synthetic.browser.event.actionDuration.load',
    'builtin:synthetic.browser.event.actionDuration.load.geo',
    'builtin:synthetic.browser.event.actionDuration.xhr',
    'builtin:synthetic.browser.event.actionDuration.xhr.geo',
    'builtin:synthetic.browser.event.cumulativeLayoutShift.load',
    'builtin:synthetic.browser.event.cumulativeLayoutShift.load.geo',
    'builtin:synthetic.browser.event.domInteractive.load',
    'builtin:synthetic.browser.event.domInteractive.load.geo',
    'builtin:synthetic.browser.event.errorCodes',
    'builtin:synthetic.browser.event.errorCodes.geo',
    'builtin:synthetic.browser.event.failure',
    'builtin:synthetic.browser.event.failure.geo',
    'builtin:synthetic.browser.event.firstByte.load',
    'builtin:synthetic.browser.event.firstByte.load.geo',
    'builtin:synthetic.browser.event.firstByte.xhr',
    'builtin:synthetic.browser.event.firstByte.xhr.geo',
    'builtin:synthetic.browser.event.largestContentfulPaint.load',
    'builtin:synthetic.browser.event.largestContentfulPaint.load.geo',
    'builtin:synthetic.browser.event.loadEventEnd.load',
    'builtin:synthetic.browser.event.loadEventEnd.load.geo',
    'builtin:synthetic.browser.event.loadEventStart.load',
    'builtin:synthetic.browser.event.loadEventStart.load.geo',
    'builtin:synthetic.browser.event.networkContribution.load',
    'builtin:synthetic.browser.event.networkContribution.load.geo',
    'builtin:synthetic.browser.event.networkContribution.xhr',
    'builtin:synthetic.browser.event.networkContribution.xhr.geo',
    'builtin:synthetic.browser.event.responseEnd.load',
    'builtin:synthetic.browser.event.responseEnd.load.geo',
    'builtin:synthetic.browser.event.responseEnd.xhr',
    'builtin:synthetic.browser.event.responseEnd.xhr.geo',
    'builtin:synthetic.browser.event.serverContribution.load',
    'builtin:synthetic.browser.event.serverContribution.load.geo',
    'builtin:synthetic.browser.event.serverContribution.xhr',
    'builtin:synthetic.browser.event.serverContribution.xhr.geo',
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
    'builtin:synthetic.browser.event.visuallyComplete.xhr',
    'builtin:synthetic.browser.event.visuallyComplete.xhr.geo',
    'builtin:synthetic.browser.failure',
    'builtin:synthetic.browser.failure.geo',
    'builtin:synthetic.browser.firstByte.load',
    'builtin:synthetic.browser.firstByte.load.geo',
    'builtin:synthetic.browser.firstByte.xhr',
    'builtin:synthetic.browser.firstByte.xhr.geo',
    'builtin:synthetic.browser.largestContentfulPaint.load',
    'builtin:synthetic.browser.largestContentfulPaint.load.geo',
    'builtin:synthetic.browser.loadEventEnd.load',
    'builtin:synthetic.browser.loadEventEnd.load.geo',
    'builtin:synthetic.browser.loadEventStart.load',
    'builtin:synthetic.browser.loadEventStart.load.geo',
    'builtin:synthetic.browser.networkContribution.load',
    'builtin:synthetic.browser.networkContribution.load.geo',
    'builtin:synthetic.browser.networkContribution.xhr',
    'builtin:synthetic.browser.networkContribution.xhr.geo',
    'builtin:synthetic.browser.responseEnd.load',
    'builtin:synthetic.browser.responseEnd.load.geo',
    'builtin:synthetic.browser.responseEnd.xhr',
    'builtin:synthetic.browser.responseEnd.xhr.geo',
    'builtin:synthetic.browser.serverContribution.load',
    'builtin:synthetic.browser.serverContribution.load.geo',
    'builtin:synthetic.browser.serverContribution.xhr',
    'builtin:synthetic.browser.serverContribution.xhr.geo',
    'builtin:synthetic.browser.speedIndex.load',
    'builtin:synthetic.browser.speedIndex.load.geo',
    'builtin:synthetic.browser.success',
    'builtin:synthetic.browser.success.geo',
    'builtin:synthetic.browser.total',
    'builtin:synthetic.browser.total.geo',
    'builtin:synthetic.browser.totalDuration',
    'builtin:synthetic.browser.totalDuration.geo',
    'builtin:synthetic.browser.visuallyComplete.load',
    'builtin:synthetic.browser.visuallyComplete.load.geo',
    'builtin:synthetic.browser.visuallyComplete.xhr',
    'builtin:synthetic.browser.visuallyComplete.xhr.geo'
]

# 実際に取得できたメトリクス（実行結果から）
RETRIEVED_METRICS = [
    'builtin:synthetic.browser.actionDuration.load',
    'builtin:synthetic.browser.actionDuration.load.geo',
    'builtin:synthetic.browser.availability',
    'builtin:synthetic.browser.availability.location.total',
    'builtin:synthetic.browser.availability.location.totalWoMaintenanceWindow',
    'builtin:synthetic.browser.cumulativeLayoutShift.load',
    'builtin:synthetic.browser.cumulativeLayoutShift.load.geo',
    'builtin:synthetic.browser.domInteractive.load',
    'builtin:synthetic.browser.domInteractive.load.geo',
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

def analyze_metrics():
    """メトリクス比較分析"""
    
    print("📊 Synthetic Browser監視メトリクス詳細比較分析")
    print("=" * 60)
    
    # 基本統計
    total_official = len(OFFICIAL_BROWSER_METRICS)
    total_retrieved = len(RETRIEVED_METRICS)
    
    print(f"\n📈 基本統計:")
    print(f"   公式記載メトリクス: {total_official}個")
    print(f"   実際取得成功: {total_retrieved}個")
    print(f"   取得成功率: {total_retrieved/total_official*100:.1f}%")
    
    # 取得できていないメトリクス
    missing_metrics = set(OFFICIAL_BROWSER_METRICS) - set(RETRIEVED_METRICS)
    print(f"\n❌ 未取得メトリクス: {len(missing_metrics)}個")
    
    # カテゴリ別分析
    categories = {
        'Custom Action': [m for m in missing_metrics if '.custom' in m],
        'XHR Action': [m for m in missing_metrics if '.xhr' in m],
        'Error系': [m for m in missing_metrics if 'errorCodes' in m],
        'Event系': [m for m in missing_metrics if '.event.' in m and '.custom' not in m and '.xhr' not in m and 'errorCodes' not in m]
    }
    
    print(f"\n🔍 未取得メトリクスのカテゴリ別分析:")
    for category, metrics in categories.items():
        print(f"   {category}: {len(metrics)}個")
        if len(metrics) <= 5:  # 5個以下なら全て表示
            for metric in sorted(metrics):
                print(f"     - {metric}")
        else:  # 多い場合は最初の3個だけ表示
            for metric in sorted(metrics)[:3]:
                print(f"     - {metric}")
            print(f"     ... 他{len(metrics)-3}個")
    
    # 取得成功メトリクスの分析
    print(f"\n✅ 取得成功メトリクスの分析:")
    
    success_categories = {
        'Core Web Vitals': [m for m in RETRIEVED_METRICS if any(x in m for x in ['largestContentfulPaint', 'cumulativeLayoutShift'])],
        'パフォーマンス': [m for m in RETRIEVED_METRICS if any(x in m for x in ['actionDuration.load', 'domInteractive', 'speedIndex', 'visuallyComplete', 'loadEvent', 'totalDuration'])],
        'ネットワーク': [m for m in RETRIEVED_METRICS if any(x in m for x in ['firstByte', 'networkContribution', 'serverContribution', 'responseEnd'])],
        '可用性': [m for m in RETRIEVED_METRICS if any(x in m for x in ['availability', 'success', 'failure', 'total'])],
        '地理的分散': [m for m in RETRIEVED_METRICS if m.endswith('.geo')]
    }
    
    for category, metrics in success_categories.items():
        print(f"   {category}: {len(metrics)}個")
    
    # 重要度評価
    print(f"\n⭐ 重要度評価:")
    critical_metrics = [
        'builtin:synthetic.browser.actionDuration.load',
        'builtin:synthetic.browser.availability',
        'builtin:synthetic.browser.largestContentfulPaint.load',
        'builtin:synthetic.browser.cumulativeLayoutShift.load',
        'builtin:synthetic.browser.firstByte.load'
    ]
    
    critical_retrieved = [m for m in critical_metrics if m in RETRIEVED_METRICS]
    print(f"   重要メトリクス取得率: {len(critical_retrieved)}/{len(critical_metrics)} ({len(critical_retrieved)/len(critical_metrics)*100:.0f}%)")
    
    for metric in critical_metrics:
        status = "✅" if metric in RETRIEVED_METRICS else "❌"
        print(f"   {status} {metric}")
    
    print(f"\n💡 結論:")
    print(f"   - 基本的なパフォーマンス監視に必要なメトリクスは取得済み")
    print(f"   - Core Web Vitals (LCP, CLS) 対応済み")
    print(f"   - 未取得メトリクスは主に特定条件依存（Custom/XHR Action、Error等）")
    print(f"   - 実用的な監視分析には十分な35個のメトリクスを確保")

if __name__ == "__main__":
    analyze_metrics() 