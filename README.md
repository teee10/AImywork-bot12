# マイワーク AIスクール サポートボット

LINEからの質問にClaudeが自動回答するボットです。

---

## セットアップ手順

### 1. 必要なもの
- [Vercelアカウント](https://vercel.com)（無料）
- [LINE Developersアカウント](https://developers.line.biz/ja/)
- Anthropic API Key

---

### 2. LINE Messaging APIの設定

1. [LINE Developers](https://developers.line.biz/ja/) にログイン
2. 「新規プロバイダー作成」→ 適当な名前をつける
3. 「Messaging APIチャネル」を作成
4. チャネル基本設定 → **Channel Secret** をメモ
5. Messaging API設定 → **Channel Access Token**（長期）を発行してメモ
6. 「応答メッセージ」をオフにする（自動応答と競合するため）

---

### 3. Vercelにデプロイ

```bash
# このフォルダをGitHubにpush（またはVercel CLIで直接デプロイ）
npm i -g vercel
vercel
```

デプロイ後にURLが発行されます（例：`https://mywork-bot.vercel.app`）

---

### 4. 環境変数をVercelに設定

Vercelダッシュボード → プロジェクト → Settings → Environment Variables に以下を追加：

| 変数名 | 値 |
|--------|-----|
| `LINE_CHANNEL_SECRET` | LINE DevelopersのChannel Secret |
| `LINE_ACCESS_TOKEN` | LINE DevelopersのChannel Access Token |
| `ANTHROPIC_API_KEY` | AnthropicのAPI Key |

追加後、**Redeployを実行**（環境変数を反映させるため）

---

### 5. LINE WebhookにURLを設定

LINE Developers → Messaging API設定 → Webhook URL に以下を入力：

```
https://あなたのVercel URL/webhook
```

例：`https://mywork-bot.vercel.app/webhook`

「検証」ボタンを押して ✅ が出ればOK

---

## 使い方

- 生徒がLINEで質問を送ると自動返信
- GoogleドキュメントのURLを送ると内容を読んでフィードバック

---

## カスタマイズ

`api/webhook.js` の `SYSTEM_PROMPT` を編集することで、
ボットの回答スタイルやFAQ内容を変更できます。
