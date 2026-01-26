# Events JSON API スキーマ

## エンドポイント

```
https://raw.githubusercontent.com/{owner}/{repo}/main/events/data/events.json
```

## レスポンス形式

### ルートオブジェクト

```json
{
  "generated_at": "2024-01-15T10:30:00+09:00",
  "timezone": "Asia/Tokyo",
  "total_count": 5,
  "events": [...]
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `generated_at` | string (ISO 8601) | JSON生成日時（JST） |
| `timezone` | string | タイムゾーン（常に "Asia/Tokyo"） |
| `total_count` | number | イベントの総数 |
| `events` | array | イベントオブジェクトの配列 |

### イベントオブジェクト

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "街頭演説",
  "date": {
    "start": "2026-01-29",
    "end": null
  },
  "location": "福岡",
  "time": "午後",
  "live_stream_url": "",
  "description": "古川　あおいアカウントよりご確認ください\nhttps://x.com/AoiFurukawa\nhttps://www.instagram.com/aoi.furukawa/",
  "notion_url": "https://www.notion.so/...",
  "created_time": "2024-01-10T12:00:00.000Z",
  "last_edited_time": "2024-01-15T10:00:00.000Z"
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `id` | string | ✓ | NotionページID |
| `name` | string | ✓ | イベント名（Notionの「名前」プロパティ） |
| `date` | object | ✓ | 日付情報 |
| `date.start` | string \| null | ✓ | 開始日時（ISO 8601形式、または日付のみ "YYYY-MM-DD"） |
| `date.end` | string \| null | ✓ | 終了日時（ISO 8601形式、または日付のみ "YYYY-MM-DD"）。単日イベントの場合は `null` |
| `location` | string | ✓ | 場所（Notionの「場所」プロパティ）。空文字列の場合あり |
| `time` | string | ✓ | 時間帯（Notionの「時間」プロパティ）。空文字列の場合あり |
| `live_stream_url` | string | ✓ | Live配信URL（Notionの「Live配信」プロパティ）。空文字列の場合あり |
| `description` | string | ✓ | 詳細説明（Notionの「詳細」プロパティ）。改行文字 `\n` を含む場合あり |
| `notion_url` | string | ✓ | NotionページのURL |
| `created_time` | string | ✓ | 作成日時（ISO 8601 UTC） |
| `last_edited_time` | string | ✓ | 最終更新日時（ISO 8601 UTC） |

## 使用例

### JavaScript (fetch)

```javascript
async function fetchEvents() {
  const response = await fetch(
    'https://raw.githubusercontent.com/{owner}/{repo}/main/events/data/events.json'
  );
  const data = await response.json();
  
  console.log(`取得件数: ${data.total_count}`);
  console.log(`生成日時: ${data.generated_at}`);
  
  data.events.forEach(event => {
    console.log(`${event.name} - ${event.date.start} @ ${event.location}`);
  });
  
  return data.events;
}
```

### TypeScript 型定義

```typescript
interface EventDate {
  start: string | null;
  end: string | null;
}

interface Event {
  id: string;
  name: string;
  date: EventDate;
  location: string;
  time: string;
  live_stream_url: string;
  description: string;
  notion_url: string;
  created_time: string;
  last_edited_time: string;
}

interface EventsResponse {
  generated_at: string;
  timezone: string;
  total_count: number;
  events: Event[];
}
```

### React コンポーネント例

```tsx
import { useEffect, useState } from 'react';

function EventsList() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://raw.githubusercontent.com/{owner}/{repo}/main/events/data/events.json')
      .then(res => res.json())
      .then(data => {
        setEvents(data.events);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>読み込み中...</div>;

  return (
    <ul>
      {events.map(event => (
        <li key={event.id}>
          <h3>{event.name}</h3>
          <p>{event.date.start} @ {event.location}</p>
          {event.live_stream_url && (
            <a href={event.live_stream_url}>Live配信を見る</a>
          )}
        </li>
      ))}
    </ul>
  );
}
```

## フィルタリング

- このAPIは**現在時刻（JST）以降のイベントのみ**を返します
- 過去のイベントは自動的に除外されます
- イベントは日付の昇順（古い順）でソートされています

## 更新頻度

- GitHub Actionsにより**5分おき**に自動更新されます
- `generated_at` フィールドで最終更新時刻を確認できます
