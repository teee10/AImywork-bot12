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
- 返答は日本語で、カジュアルすぎず堅すぎないトーンで

## よくある質問
- ツールの使い方がわからない → 公式チュートリアルを案内し、具体的なステップを説明
- 課題提出の方法 → GoogleドキュメントにまとめてリンクをLINEで送るよう案内
- 次のステップが知りたい → カリキュラムの順序を案内`;

const GOOGLE_DOC_REGEX = /https:\/\/docs\.google\.com\/document\/d\/([a-zA-Z0-9_-]+)/;

// LINE署名検証
function verifySignature(body, signature) {
  const hash = crypto
    .createHmac("sha256", LINE_CHANNEL_SECRET)
    .update(body)
    .digest("base64");
  return hash === signature;
}

// Google Docsのテキスト取得
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

// Claude APIに問い合わせ
async function askClaude(userText) {
  // Google DocsのURLがあれば内容を取得して追加
  let content = userText;
  const docMatch = userText.match(GOOGLE_DOC_REGEX);
  if (docMatch) {
    const docContent = await fetchGoogleDoc(docMatch[0]);
    if (docContent) {
      content = `${userText}\n\n【Googleドキュメントの内容】\n${docContent.slice(0, 4000)}`;
    } else {
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
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content }],
    }),
  });

  const data = await res.json();
  return data.content?.[0]?.text || "申し訳ありません、回答を生成できませんでした。";
}

// LINEに返信
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

// Vercel Serverless Function のエントリーポイント
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(200).json({ status: "ok" });
  }

  // 署名検証
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
      await replyToLine(replyToken, "エラーが発生しました。しばらくしてからもう一度お試しください。");
    }
  }

  res.status(200).json({ status: "ok" });
}
