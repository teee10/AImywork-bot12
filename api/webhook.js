import crypto from "crypto";

const LINE_CHANNEL_SECRET = process.env.LINE_CHANNEL_SECRET;
const LINE_ACCESS_TOKEN = process.env.LINE_ACCESS_TOKEN;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const FEEDBACK_DOC_ID = "10ODxEZ3L7E3qMor2RN3E1wS7s1t00S7ICeNl6WKmjZA";
const GOOGLE_DOC_REGEX = /https:\/\/docs\.google\.com\/document\/d\/([a-zA-Z0-9_-]+)/;

let feedbackExamplesCache = null;
let cacheLoadedAt = null;
const CACHE_TTL = 1000 * 60 * 60; // 1時間キャッシュ

// 起動時に非同期で先読み（タイムアウトしても処理は続行）
async function loadFeedbackExamples() {
  if (feedbackExamplesCache && cacheLoadedAt && Date.now() - cacheLoadedAt < CACHE_TTL) {
    return feedbackExamplesCache;
  }
  try {
    const url = `https://docs.google.com/document/d/${FEEDBACK_DOC_ID}/export?format=txt`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000); // 5秒でタイムアウト
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) return feedbackExamplesCache || "";
    const text = await res.text();
    feedbackExamplesCache = text.slice(0, 8000);
    cacheLoadedAt = Date.now();
    return feedbackExamplesCache;
  } catch {
    return feedbackExamplesCache || ""; // 失敗してもキャッシュがあれば使う
  }
}

function buildSystemPrompt(feedbackExamples) {
  return `あなたは「マイワーク AIスクール」の生徒サポートAIアシスタントです。
講師の代わりに生徒からの質問への回答と、課題への詳細なフィードバックを行います。

## スクールについて
コース内容はAIライティング・画像生成AI・動画生成AI・プロンプトエンジニアリングです。
使用ツールはRunway Gen-3・Pika Labs・Kling AI・Sora・ChatGPT・Midjourneyなどです。

## 通常質問への対応
生徒が課題や教材について質問したら、わかりやすく丁寧に答えてください。
わからないことは「講師に確認します」と正直に伝えてください。
返答は日本語で、カジュアルすぎず堅すぎないトーンで。
スクールと関係のない話題には「スクールのサポートボットなので、課題やツールに関する質問をどうぞ」と返してください。

## 課題フィードバックのルール（最重要）

文体ルールとして、箇条書きと太字は一切使わず全て文章で書くこと。良かった点は何がなぜ良いのかまで掘り下げること。改善点はどう直せばよいかまで説明すること。初心者を傷つけない励ましのトーンを維持すること。どのAIツールを使ったか特定・推測するコメントは一切しないこと。点数は高く出しすぎないこと（平均的な課題は75〜83点程度）。一度フィードバックした課題が再送されても同じ内容・点数で返すこと（課題内容が変わっていれば再フィードバックする）。

フォーマットとして、冒頭は必ず「フィードバックします！」から始めること。総合点を「総合点：〇〇点」の形式で出すこと（複数作品は各作品に「総合評価：〇〇点」）。課題タイプを自動判定して該当する全観点から超詳細にフィードバックすること。全て文章で書き箇条書きと太字は一切使わないこと。最後は全体総括と励ましで締めること。

## フィードバック文体・知識の参考
${feedbackExamples ? feedbackExamples : "（参考例文は現在読み込み中です）"}`;
}

async function fetchGoogleDoc(url) {
  const match = url.match(GOOGLE_DOC_REGEX);
  if (!match) return null;
  const docId = match[1];
  if (docId === FEEDBACK_DOC_ID) return null;
  try {
    const exportUrl = `https://docs.google.com/document/d/${docId}/export?format=txt`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    const res = await fetch(exportUrl, { signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  }
}

async function fetchLineImage(messageId) {
  const res = await fetch(`https://api-data.line.me/v2/bot/message/${messageId}/content`, {
    headers: { Authorization: `Bearer ${LINE_ACCESS_TOKEN}` },
  });
  if (!res.ok) return null;
  const buffer = await res.arrayBuffer();
  return Buffer.from(buffer).toString("base64");
}

async function askClaude(userContent, isImage = false) {
  const feedbackExamples = await loadFeedbackExamples();
  const systemPrompt = buildSystemPrompt(feedbackExamples);

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
        let content = msg.text;
        const docMatch = msg.text.match(GOOGLE_DOC_REGEX);
        if (docMatch) {
          const docContent = await fetchGoogleDoc(docMatch[0]);
          if (docContent) {
            content = `${msg.text}\n\n【Googleドキュメントの内容】\n${docContent.slice(0, 4000)}`;
          } else {
            content = `${msg.text}\n\n※ Googleドキュメントの読み取りに失敗しました。「リンクを知っている全員が閲覧可能」に設定されているか確認してください。`;
          }
        }
        const reply = await askClaude(content);
        await replyToLine(replyToken, reply);

      } else if (msg.type === "image") {
        const base64Image = await fetchLineImage(msg.id);
        if (!base64Image) {
          await replyToLine(replyToken, "画像の取得に失敗しました。もう一度送ってみてください。");
          continue;
        }
        const userContent = [
          { type: "image", source: { type: "base64", media_type: "image/jpeg", data: base64Image } },
          { type: "text", text: "課題画像が送られました。画像生成AI・バナー・インスタグラム投稿などの課題として超詳細にフィードバックしてください。" },
        ];
        const reply = await askClaude(userContent, true);
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
