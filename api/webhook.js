import crypto from "crypto";

const LINE_CHANNEL_SECRET = process.env.LINE_CHANNEL_SECRET;
const LINE_ACCESS_TOKEN = process.env.LINE_ACCESS_TOKEN;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const FEEDBACK_DOC_ID = "10ODxEZ3L7E3qMor2RN3E1wS7s1t00S7ICeNl6WKmjZA";
const GOOGLE_DOC_REGEX = /https:\/\/docs\.google\.com\/document\/d\/([a-zA-Z0-9_-]+)/;

// フィードバック例文キャッシュ
let feedbackExamplesCache = null;

async function fetchFeedbackExamples() {
  if (feedbackExamplesCache) return feedbackExamplesCache;
  try {
    const url = `https://docs.google.com/document/d/${FEEDBACK_DOC_ID}/export?format=txt`;
    const res = await fetch(url);
    if (!res.ok) return "";
    const text = await res.text();
    feedbackExamplesCache = text.slice(0, 6000);
    return feedbackExamplesCache;
  } catch {
    return "";
  }
}

function buildSystemPrompt(feedbackExamples) {
  return `あなたは「マイワーク AIスクール」の生徒サポートAIアシスタントです。
講師の代わりに生徒からの質問への回答と、課題へのフィードバックを行います。

## スクールについて
- コース内容：AIライティング、画像生成AI、動画生成AI、プロンプトエンジニアリング
- 使用ツール：Runway Gen-3、Pika Labs、Kling AI、Sora、ChatGPT、Midjourneyなど
- 受講形式：オンライン、テキストベースのカリキュラム

## 通常質問への対応
- 生徒が課題や教材について質問したら、わかりやすく丁寧に答える
- わからないことは「講師に確認します」と正直に伝える
- 返答は日本語で、カジュアルすぎず堅すぎないトーンで

## 課題フィードバックのルール（最重要）
課題（プロンプト・記事・インスタグラム投稿・画像生成・動画生成など）へのフィードバックは以下のルールを必ず守ること。

### 文体ルール
- 箇条書き（・や-）は一切使わない
- 太字（**）は一切使わない
- 全て文章（散文）で書く
- 良かった点は具体的に、何がなぜ良いのかまで説明する
- 改善点も具体的に、どう直せばよいかまで説明する
- 初心者を傷つけない励ましのトーンを維持する
- どのAIツールを使ったか特定・推測するコメントは一切しない

### フォーマット
1. 冒頭は必ず「フィードバックします！」から始める
2. 総合点を「総合点：〇〇点」の形式で出す（複数作品は各作品に「総合評価：〇〇点」）
3. 「良かった点からお伝えします。」の後に良かった点を文章で詳しく書く
4. 「改善できる点をお伝えします。」の後に改善点を文章で詳しく書く
5. 全体総括と励ましで締める

## フィードバック文体の参考例
以下は講師が実際に書いたフィードバックの例です。この文体・トーン・詳しさを参考にしてください。

${feedbackExamples}`;
}

async function fetchGoogleDoc(url) {
  const match = url.match(GOOGLE_DOC_REGEX);
  if (!match) return null;
  const docId = match[1];
  if (docId === FEEDBACK_DOC_ID) return null; // 参考例文ドキュメントはスキップ
  const exportUrl = `https://docs.google.com/document/d/${docId}/export?format=txt`;
  try {
    const res = await fetch(exportUrl);
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  }
}

async function askClaude(userText) {
  const feedbackExamples = await fetchFeedbackExamples();
  const systemPrompt = buildSystemPrompt(feedbackExamples);

  let content = userText;
  const docMatch = userText.match(GOOGLE_DOC_REGEX);
  if (docMatch) {
    const docContent = await fetchGoogleDoc(docMatch[0]);
    if (docContent) {
      content = `${userText}\n\n【Googleドキュメントの内容】\n${docContent.slice(0, 4000)}`;
    } else if (docContent === null && docMatch[1] !== FEEDBACK_DOC_ID) {
      content = `${userText}\n\n※ Googleドキュメントの読み取りに失敗しました。「リンクを知っている全員が閲覧可能」に設定されているか確認してください。`;
    }
  }

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-5",
      max_tokens: 2000,
      system: systemPrompt,
      messages: [{ role: "user", content }],
    }),
  });

  const data = await res.json();

  if (!res.ok || data.error) {
    throw new Error(`API Error ${res.status}: ${JSON.stringify(data.error)}`);
  }

  return data.content?.[0]?.text || "返答を取得できませんでした。";
}

async function replyToLine(replyToken, text) {
  // LINEは1メッセージ最大5000文字なので超える場合は分割
  const MAX_LENGTH = 4500;
  const messages = [];
  let remaining = text;
  while (remaining.length > 0) {
    messages.push({ type: "text", text: remaining.slice(0, MAX_LENGTH) });
    remaining = remaining.slice(MAX_LENGTH);
    if (messages.length >= 5) break; // LINEは1回のreplyで最大5メッセージ
  }

  await fetch("https://api.line.me/v2/bot/message/reply", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${LINE_ACCESS_TOKEN}`,
    },
    body: JSON.stringify({ replyToken, messages }),
  });
}

function verifySignature(body, signature) {
  const hash = crypto
    .createHmac("sha256", LINE_CHANNEL_SECRET)
    .update(body)
    .digest("base64");
  return hash === signature;
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(200).json({ status: "ok" });
  }

  const signature = req.headers["x-line-signature"];
  const rawBody = JSON.stringify(req.body);
  if (!verifySignature(rawBody, signature)) {
    return res.status(401).json({ error: "Invalid signature" });
  }

  const events = req.body.events || [];

  for (const event of events) {
    if (event.type !== "message" || event.message.type !== "text") continue;

    const userText = event.message.text;
    const replyToken = event.replyToken;

    try {
      const reply = await askClaude(userText);
      await replyToLine(replyToken, reply);
    } catch (err) {
      console.error("Error:", err);
      await replyToLine(replyToken, `エラー詳細: ${err.message}`);
    }
  }

  res.status(200).json({ status: "ok" });
