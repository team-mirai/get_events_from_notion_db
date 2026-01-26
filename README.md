# Events API

Notion データベースからイベント情報を取得し、JSON API として公開するプロジェクトです。

## 概要

- **定期実行**: GitHub Actions により5分おきに自動実行
- **データソース**: Notion API 経由でイベントデータベースから取得
- **フィルタリング**: 日本時間（JST）の現在時刻以降のイベントのみを抽出
- **出力**: `data/events.json` として保存・公開

## API エンドポイント

JSON データは以下の URL から取得可能です：

### GitHub Raw URL（推奨）
```
https://raw.githubusercontent.com/{owner}/{repo}/main/events/data/events.json
```

### GitHub Pages（設定した場合）
```
https://{owner}.github.io/{repo}/events/data/events.json
```

## セットアップ

### 1. Notion Integration の作成

1. [Notion Developers](https://www.notion.so/my-integrations) にアクセス
2. 「New integration」をクリック
3. Integration の名前を設定（例: "Events API"）
4. 「Submit」をクリック
5. 表示される「Internal Integration Token」をコピー

### 2. Notion データベースの準備

1. イベント用のデータベースを作成（または既存のものを使用）
2. 以下のプロパティを設定（名前は調整可能）:
   - `Name` または `Title`: タイトル（タイトル型）
   - `Date`: 日時（日付型）
   - `Location` または `場所`: 場所（テキスト型）
   - `Description` または `説明`: 説明（テキスト型）
   - `URL` または `Link`: リンク（URL型）
   - `Category` または `カテゴリ`: カテゴリ（セレクト型）

3. データベースに Integration を接続:
   - データベースページ右上の「...」をクリック
   - 「Connections」→「Add connections」
   - 作成した Integration を選択

4. データベース ID を取得:
   - データベースページの URL から ID を取得
   - `https://www.notion.so/{workspace}/{database_id}?v=...`

### 3. GitHub Secrets の設定

リポジトリの Settings → Secrets and variables → Actions で以下を設定:

| Secret 名 | 説明 |
|-----------|------|
| `NOTION_API_TOKEN` | Notion Integration Token |
| `NOTION_DATABASE_ID` | Notion データベースの ID |

### 4. ワークフローの有効化

1. このディレクトリをリポジトリにプッシュ
2. GitHub Actions タブでワークフローを有効化
3. 手動実行でテスト: Actions → "Fetch Events from Notion" → "Run workflow"

## JSON 出力形式

```json
{
  "generated_at": "2024-01-15T10:30:00+09:00",
  "timezone": "Asia/Tokyo",
  "total_count": 5,
  "events": [
    {
      "id": "page-id-xxx",
      "title": "イベント名",
      "date_start": "2024-01-20T14:00:00+09:00",
      "date_end": "2024-01-20T17:00:00+09:00",
      "location": "東京都渋谷区...",
      "description": "イベントの説明...",
      "url": "https://example.com/event",
      "category": "セミナー",
      "notion_url": "https://www.notion.so/...",
      "last_edited": "2024-01-10T12:00:00.000Z"
    }
  ]
}
```

## フロントエンドでの利用例

### JavaScript (fetch)

```javascript
async function fetchEvents() {
  const response = await fetch(
    'https://raw.githubusercontent.com/{owner}/{repo}/main/events/data/events.json'
  );
  const data = await response.json();
  return data.events;
}
```

### React/Next.js

```typescript
const [events, setEvents] = useState([]);

useEffect(() => {
  fetch('https://raw.githubusercontent.com/{owner}/{repo}/main/events/data/events.json')
    .then(res => res.json())
    .then(data => setEvents(data.events));
}, []);
```

## カスタマイズ

### プロパティ名の変更

`fetch_events.py` の `parse_event()` 関数内で、実際の Notion データベースのプロパティ名に合わせて調整してください：

```python
# 例: "イベント名" というプロパティ名を使う場合
title_prop = properties.get("イベント名")
```

### 追加のプロパティ取得

新しいフィールドを追加する場合は、`parse_event()` 関数に追加処理を記述してください。

## トラブルシューティング

### API Token エラー
- Secrets が正しく設定されているか確認
- Token に余分なスペースがないか確認

### データベースアクセスエラー
- Integration がデータベースに接続されているか確認
- データベース ID が正しいか確認

### 日付フィルタリングが効かない
- データベースの日付プロパティ名が "Date" か確認
- 異なる場合は `fetch_events.py` を修正

## ライセンス

MIT License
