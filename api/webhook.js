import crypto from "crypto";

const LINE_CHANNEL_SECRET = process.env.LINE_CHANNEL_SECRET;
const LINE_ACCESS_TOKEN = process.env.LINE_ACCESS_TOKEN;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const SYSTEM_PROMPT = `あなたは「マイワーク AIスクール」の生徒サポートAIアシスタントです。
講師の代わりに生徒からの質問に丁寧に答えてください。

## スクールについて
- コース内容：AIライティング、画像生成AI、動画生成AI、プロンプトエンジニアリング
- 使用ツール：Runway Gen-3、Pika Labs、Kling AI、Sora、ChatGPT、Midjourneyなど
- 受講形式：オンライン、テキストベースのカリキュラム

## 対応方針
- 生徒が課題や教材について質問したら、わかりやすく丁寧に答える
- Googleドキュメントの内容が共有されたら、その内容をもとに具体的にフィードバックする
- 課題のフィードバックは励ましを忘れずに、改善点も具体的に伝える
- わからないことは「講師に確認します」と正直に伝える
- 返答は日本語で、カジュアルすぎず堅すぎないトーンで`;

const GOOGLE_DOC_REGEX = /https:\/\/docs\.google\.com\/document\/d\/([a-zA-Z0-9_-]+)/;

function verifySignature(body, signature) {
  const hash = crypto
    .createHmac("sha256", LINE_CHANNEL_SECRET)
    .update(body)
    .digest("base64");
  return hash === signature;
}

async function fetchGoogleDoc(url) {
  const match = url.match(GOOGLE_DOC_REGEX);
  if (!match) return null;
  const docId = match[1];
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
  let content = userText;
  const docMatch = userText.match(GOOGLE_DOC_REGEX);
  if (docMatch) {
    const docContent = await fetchGoogleDoc(docMatch[0]);
    if (docContent) {
      content = `${userText}\n\n【Googleドキュメントの内容】\n${docContent.slice(0, 4000)}`;
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
      max_tokens: 1000,
      system: SYSTEM_PROMPT,
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
  await fetch("https://api.line.me/v2/bot/message/reply", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${LINE_ACCESS_TOKEN}`,
    },
    body: JSON.stringify({
      replyToken,
      messages: [{ type: "text", text }],
    }),
  });
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
}
