import crypto from "crypto";

const LINE_CHANNEL_SECRET = process.env.LINE_CHANNEL_SECRET;
const LINE_ACCESS_TOKEN = process.env.LINE_ACCESS_TOKEN;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const FEEDBACK_DOC_ID = "10ODxEZ3L7E3qMor2RN3E1wS7s1t00S7ICeNl6WKmjZA";
const GOOGLE_DOC_REGEX = /https:\/\/docs\.google\.com\/document\/d\/([a-zA-Z0-9_-]+)/;

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
講師の代わりに生徒からの質問への回答と、課題への詳細なフィードバックを行います。

## スクールについて
- コース内容：AIライティング、画像生成AI、動画生成AI、プロンプトエンジニアリング
- 使用ツール：Runway Gen-3、Pika Labs、Kling AI、Sora、ChatGPT、Midjourneyなど
- 受講形式：オンライン、テキストベースのカリキュラム

## 通常質問への対応
- 生徒が課題や教材について質問したら、わかりやすく丁寧に答える
- わからないことは「講師に確認します」と正直に伝える
- 返答は日本語で、カジュアルすぎず堅すぎないトーンで
- スクールと関係のない話題には「スクールのサポートボットなので、課題やツールに関する質問をどうぞ」と返す

## 課題フィードバックのルール（最重要）

### 文体ルール（絶対に守ること）
- 箇条書き（・や-）は一切使わない
- 太字（**）は一切使わない
- 全て文章（散文）で書く
- 良かった点は具体的に、何がなぜ良いのかまで掘り下げて説明する
- 改善点も具体的に、どう直せばよいかまで説明する
- 初心者を傷つけない励ましのトーンを維持する
- どのAIツールを使ったか特定・推測するコメントは一切しない
- 点数は高く出しすぎない（平均的な課題は75〜83点程度）
- 一度フィードバックした課題が再送されても同じ内容・点数で返す（課題内容が変わっていれば再フィードバックする）

### フォーマット
冒頭は必ず「フィードバックします！」から始める。
総合点を「総合点：〇〇点」の形式で出す（複数作品は各作品に「総合評価：〇〇点」）。
その後、課題タイプを自動判定して該当する全観点から超詳細にフィードバックする。
全て文章（散文）で書き、箇条書きと太字は一切使わない。
最後は全体総括と励ましで締める。

## フィードバック文体の参考例
以下は講師が実際に書いたフィードバックの例です。この文体・トーン・詳しさを参考にしてください。

${feedbackExamples}`;
}

async function fetchGoogleDoc(url) {
  const match = url.match(GOOGLE_DOC_REGEX);
  if (!match) return null;
  const docId = match[1];
  if (docId === FEEDBACK_DOC_ID) return null;
  const exportUrl = `https://docs.google.com/document/d/${docId}/export?format=txt`;
  try {
    const res = await fetch(exportUrl);
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  }
}

// LINE画像をBase64で取得
async function fetchLineImage(messageId) {
  const res = await fetch(`https://api-data.line.me/v2/bot/message/${messageId}/content`, {
    headers: { Authorization: `Bearer ${LINE_ACCESS_TOKEN}` },
  });
  if (!res.ok) return null;
  const buffer = await res.arrayBuffer();
  const base64 = Buffer.from(buffer).toString("base64");
  return base64;
}

// テキストのみでClaudeに問い合わせ
async function askClaudeText(userText) {
  const feedbackExamples = await fetchFeedbackExamples();
  const systemPrompt = buildSystemPrompt(feedbackExamples);

  let content = userText;
  const docMatch = userText.match(GOOGLE_DOC_REGEX);
  if (docMatch) {
    const docContent = await fetchGoogleDoc(docMatch[0]);
    if (docContent) {
      content = `${userText}\n\n【Googleドキュメントの内容】\n${docContent.slice(0, 4000)}`;
    } else if (docMatch[1] !== FEEDBACK_DOC_ID) {
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

// 画像付きでClaudeに問い合わせ
async function askClaudeImage(base64Image, caption) {
  const feedbackExamples = await fetchFeedbackExamples();
  const systemPrompt = buildSystemPrompt(feedbackExamples);

  const userContent = [
    {
      type: "image",
      source: {
        type: "base64",
        media_type: "image/jpeg",
        data: base64Image,
      },
    },
    {
      type: "text",
      text: caption
        ? `課題画像が送られました。キャプション：「${caption}」\nこの画像に対して超詳細なフィードバックをしてください。`
        : "課題画像が送られました。この画像（画像生成AI・バナー・インスタグラム投稿など）に対して超詳細なフィードバックをしてください。",
    },
  ];

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
      messages: [{ role: "user", content: userContent }],
    }),
  });

  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(`API Error ${res.status}: ${JSON.stringify(data.error)}`);
  }
  return data.content?.[0]?.text || "返答を取得できませんでした。";
}

async function replyToLine(replyToken, text) {
  const MAX_LENGTH = 4500;
  const messages = [];
  let remaining = text;
  while (remaining.length > 0) {
    messages.push({ type: "text", text: remaining.slice(0, MAX_LENGTH) });
    remaining = remaining.slice(MAX_LENGTH);
    if (messages.length >= 5) break;
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
    if (event.type !== "message") continue;

    const replyToken = event.replyToken;
    const msg = event.message;

    try {
      if (msg.type === "text") {
        const reply = await askClaudeText(msg.text);
        await replyToLine(replyToken, reply);
      } else if (msg.type === "image") {
        const base64Image = await fetchLineImage(msg.id);
        if (!base64Image) {
          await replyToLine(replyToken, "画像の取得に失敗しました。もう一度送ってみてください。");
          continue;
        }
        const caption = msg.contentMetadata?.caption || null;
        const reply = await askClaudeImage(base64Image, caption);
        await replyToLine(replyToken, reply);
      } else {
        await replyToLine(replyToken, "テキストまたは画像を送ってください。課題のフィードバックや質問に対応します！");
      }
    } catch (err) {
      console.error("Error:", err);
      await replyToLine(replyToken, `エラー詳細: ${err.message}`);
    }
  }

  res.status(200).json({ status: "ok" });
}
