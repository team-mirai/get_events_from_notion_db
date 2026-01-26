#!/usr/bin/env python3
"""
Notion APIからイベント情報を取得し、現在時刻以降のイベントをJSONとして保存するスクリプト
"""

import json
import os
from datetime import datetime, timezone, timedelta
from notion_client import Client

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))


def get_notion_client():
    """Notion APIクライアントを初期化"""
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        raise ValueError("NOTION_API_TOKEN environment variable is not set")
    return Client(auth=token)


def fetch_events_from_notion(notion: Client, database_id: str) -> list:
    """
    NotionデータベースからJSTの現在時刻以降のイベントのみ取得
    """
    now_jst = datetime.now(JST)
    
    # 今日の日付（YYYY-MM-DD形式）を取得
    today_date = now_jst.date().isoformat()
    
    # Notion APIでフィルタリング（日付プロパティ名: "日付"）
    # 今日以降の日付のイベントを取得
    response = notion.databases.query(
        database_id=database_id,
        filter={
            "property": "日付",
            "date": {
                "on_or_after": today_date
            }
        },
        sorts=[
            {
                "property": "日付",
                "direction": "ascending"
            }
        ]
    )
    
    results = response.get("results", [])
    
    # ページネーション対応（100件以上の場合）
    while response.get("has_more"):
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "日付",
                "date": {
                    "on_or_after": today_date
                }
            },
            sorts=[
                {
                    "property": "日付",
                    "direction": "ascending"
                }
            ],
            start_cursor=response.get("next_cursor")
        )
        results.extend(response.get("results", []))
    
    return results


def parse_event(page: dict) -> dict:
    """
    Notionページデータをイベントオブジェクトに変換
    実際のプロパティ名に基づいて実装
    """
    properties = page.get("properties", {})
    
    # 名前（タイトル）の取得
    name = ""
    name_prop = properties.get("名前")
    if name_prop and name_prop.get("title"):
        name = "".join([t.get("plain_text", "") for t in name_prop["title"]])
    
    # 日付の取得
    date_start = None
    date_end = None
    date_prop = properties.get("日付")
    if date_prop and date_prop.get("date"):
        date_data = date_prop["date"]
        date_start = date_data.get("start")
        date_end = date_data.get("end")
    
    # 場所の取得
    location = ""
    location_prop = properties.get("場所")
    if location_prop and location_prop.get("rich_text"):
        location = "".join([t.get("plain_text", "") for t in location_prop["rich_text"]])
    
    # 時間の取得
    time = ""
    time_prop = properties.get("時間")
    if time_prop and time_prop.get("rich_text"):
        time = "".join([t.get("plain_text", "") for t in time_prop["rich_text"]])
    
    # Live配信（URL）の取得
    live_stream_url = ""
    live_prop = properties.get("Live配信")
    if live_prop:
        if live_prop.get("url"):
            live_stream_url = live_prop["url"]
        elif live_prop.get("rich_text"):
            live_stream_url = "".join([t.get("plain_text", "") for t in live_prop["rich_text"]])
    
    # 詳細の取得
    description = ""
    detail_prop = properties.get("詳細")
    if detail_prop and detail_prop.get("rich_text"):
        description = "".join([t.get("plain_text", "") for t in detail_prop["rich_text"]])
    
    return {
        "id": page.get("id", ""),
        "name": name,
        "date": {
            "start": date_start,
            "end": date_end
        },
        "location": location,
        "time": time,
        "live_stream_url": live_stream_url,
        "description": description,
        "notion_url": page.get("url", ""),
        "created_time": page.get("created_time", ""),
        "last_edited_time": page.get("last_edited_time", "")
    }


def filter_future_events(events: list, now_jst: datetime) -> list:
    """
    現在時刻以降のイベントのみをフィルタリング
    日付のみの場合は今日の日付なら全て含める（時刻情報がないため）
    """
    filtered = []
    
    for event in events:
        date_start = event.get("date", {}).get("start")
        if not date_start:
            continue
        
        # 日付文字列をパース
        try:
            # ISO形式（時刻含む）の場合
            if "T" in date_start:
                event_datetime = datetime.fromisoformat(date_start.replace("Z", "+00:00"))
                # JSTに変換（UTCの場合は）
                if event_datetime.tzinfo is None:
                    event_datetime = event_datetime.replace(tzinfo=JST)
                elif event_datetime.tzinfo.utcoffset(event_datetime).total_seconds() == 0:
                    event_datetime = event_datetime.replace(tzinfo=timezone.utc).astimezone(JST)
                # 現在時刻以降かチェック
                if event_datetime >= now_jst:
                    filtered.append(event)
            else:
                # 日付のみ（YYYY-MM-DD）の場合
                event_date = datetime.strptime(date_start, "%Y-%m-%d").date()
                today_date = now_jst.date()
                # 今日以降の日付なら含める
                if event_date >= today_date:
                    filtered.append(event)
        except (ValueError, AttributeError) as e:
            print(f"Warning: Could not parse date '{date_start}': {e}")
            continue
    
    return filtered


def main():
    """メイン処理"""
    # デバッグ: 環境変数の存在確認（値は出力しない）
    print("=== Environment Variable Check ===")
    token = os.environ.get("NOTION_API_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")
    
    print(f"NOTION_API_TOKEN: {'SET' if token else 'NOT SET'} (length: {len(token) if token else 0})")
    print(f"NOTION_DATABASE_ID: {'SET' if database_id else 'NOT SET'} (length: {len(database_id) if database_id else 0})")
    print("==================================")
    
    # 環境変数からデータベースIDを取得
    if not database_id:
        raise ValueError("NOTION_DATABASE_ID environment variable is not set")
    
    if not token:
        raise ValueError("NOTION_API_TOKEN environment variable is not set")
    
    # Notionクライアントを初期化
    notion = get_notion_client()
    
    # 現在時刻（JST）を取得
    now_jst = datetime.now(JST)
    
    # イベントを取得
    print(f"Fetching events from Notion database: {database_id}")
    print(f"Current time (JST): {now_jst.isoformat()}")
    raw_events = fetch_events_from_notion(notion, database_id)
    print(f"Found {len(raw_events)} events from today onwards")
    
    # イベントをパース
    parsed_events = [parse_event(page) for page in raw_events]
    
    # 現在時刻以降のイベントのみをフィルタリング
    events = filter_future_events(parsed_events, now_jst)
    print(f"Filtered to {len(events)} events after current time")
    
    # 出力データを作成
    output = {
        "generated_at": now_jst.isoformat(),
        "timezone": "Asia/Tokyo",
        "total_count": len(events),
        "events": events
    }
    
    # JSONファイルに保存
    output_path = "data/events.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Events saved to {output_path}")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
