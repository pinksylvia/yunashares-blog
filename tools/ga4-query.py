#!/usr/bin/env python3
"""
GA4 Data API query tool
Usage:
  python ga4-query.py top              # 今日熱門頁面 Top 10
  python ga4-query.py top 7d           # 過去 7 天熱門頁面
  python ga4-query.py page <關鍵字>     # 搜尋特定頁面
  python ga4-query.py page coupang 30d # 過去 30 天搜尋 coupang
  python ga4-query.py overview         # 今日總覽（活躍使用者、瀏覽、來源）
"""

import sys
import os
from datetime import datetime
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    Filter,
    FilterExpression,
)
from google.oauth2 import service_account

# ===== 設定 =====
PROPERTY_ID = "504824471"  # 你的 GA4 Property ID（之後填入）
KEY_FILE = os.path.expanduser("~/.ga4-key.json")  # 服務帳戶金鑰存放路徑


def get_client():
    if not os.path.exists(KEY_FILE):
        print(f"❌ 找不到金鑰檔：{KEY_FILE}")
        print("請依照設定指引下載 service account JSON 並放到此路徑")
        sys.exit(1)
    creds = service_account.Credentials.from_service_account_file(KEY_FILE)
    return BetaAnalyticsDataClient(credentials=creds)


def parse_range(s):
    """e.g. '7d' -> '7daysAgo', '30d' -> '30daysAgo', 'today' -> 'today'"""
    if s == "today":
        return "today", "today"
    if s.endswith("d"):
        return f"{s[:-1]}daysAgo", "today"
    if s == "yesterday":
        return "yesterday", "yesterday"
    return s, "today"


def top_pages(date_range="today"):
    client = get_client()
    start, end = parse_range(date_range)
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
        limit=10,
    )
    response = client.run_report(request)
    print(f"\n📊 Top 10 頁面（{date_range}）\n")
    print(f"{'瀏覽':>6}  {'使用者':>6}  標題 / 路徑")
    print("-" * 80)
    for row in response.rows:
        title = row.dimension_values[0].value[:40]
        path = row.dimension_values[1].value[:40]
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f"{views:>6}  {users:>6}  {title}")
        print(f"{'':>14}  {path}")


def search_page(keyword, date_range="today"):
    client = get_client()
    start, end = parse_range(date_range)
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers"), Metric(name="userEngagementDuration")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    match_type=Filter.StringFilter.MatchType.CONTAINS,
                    value=keyword,
                    case_sensitive=False,
                ),
            )
        ),
        order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
        limit=20,
    )
    response = client.run_report(request)
    print(f"\n🔍 包含 '{keyword}' 的頁面（{date_range}）\n")
    if not response.rows:
        print("  （沒有結果，試試在 pageTitle 也搜搜看）")
        # 加一個 title 的 fallback
        request2 = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="pageTitle",
                    string_filter=Filter.StringFilter(
                        match_type=Filter.StringFilter.MatchType.CONTAINS,
                        value=keyword,
                        case_sensitive=False,
                    ),
                )
            ),
            order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
            limit=20,
        )
        response = client.run_report(request2)
    print(f"{'瀏覽':>6}  {'使用者':>6}  標題 / 路徑")
    print("-" * 80)
    for row in response.rows:
        title = row.dimension_values[0].value[:50]
        path = row.dimension_values[1].value[:60]
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f"{views:>6}  {users:>6}  {title}")
        print(f"{'':>14}  {path}")


def overview(date_range="today"):
    client = get_client()
    start, end = parse_range(date_range)
    # 總覽指標
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="screenPageViews"),
            Metric(name="sessions"),
            Metric(name="averageSessionDuration"),
        ],
        date_ranges=[DateRange(start_date=start, end_date=end)],
    )
    response = client.run_report(request)
    if response.rows:
        m = response.rows[0].metric_values
        print(f"\n📊 總覽（{date_range}）")
        print("-" * 40)
        print(f"  活躍使用者：{m[0].value}")
        print(f"  瀏覽次數：  {m[1].value}")
        print(f"  工作階段：  {m[2].value}")
        avg_dur = float(m[3].value)
        print(f"  平均停留：  {avg_dur:.0f} 秒（{avg_dur/60:.1f} 分鐘）")

    # 流量來源
    request2 = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
        limit=10,
    )
    response2 = client.run_report(request2)
    print(f"\n🚪 流量來源")
    print("-" * 40)
    for row in response2.rows:
        ch = row.dimension_values[0].value
        s = row.metric_values[0].value
        print(f"  {s:>6}  {ch}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "top":
        top_pages(sys.argv[2] if len(sys.argv) > 2 else "today")
    elif cmd == "page":
        if len(sys.argv) < 3:
            print("Usage: python ga4-query.py page <關鍵字> [date_range]")
            sys.exit(1)
        kw = sys.argv[2]
        rng = sys.argv[3] if len(sys.argv) > 3 else "today"
        search_page(kw, rng)
    elif cmd == "overview":
        overview(sys.argv[2] if len(sys.argv) > 2 else "today")
    else:
        print(__doc__)
