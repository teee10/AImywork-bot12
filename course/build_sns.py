#!/usr/bin/env python3
"""「AI×SNS運用代行完全習得講座」PDF ビルダー。

course/content_sns/*.txt に書かれた独自記法のテキストを読み込み、
色分けされた学習教材PDFを生成する。実際の組版処理は course/engine.py。

    python course/build_sns.py

出力: manuals/AI×SNS運用代行完全習得講座.pdf
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import engine

CONFIG = {
    "title": "AI×SNS運用代行完全習得講座",
    "subtitle": "X／Instagram／Threads／TikTokの運用代行でお金を稼ぐための実務書",
    "out_path": os.path.join(ROOT, "manuals", "AI×SNS運用代行完全習得講座.pdf"),
    "content_dir": os.path.join(HERE, "content_sns"),
    "org_line": "マイワーク AIスクール",
    "default_theme_key": "base",
    "study_plan_theme_key": "ops",
    "part_colors": {
        "base": "#2B5CE6",    # 基礎編・ブルー
        "x": "#111827",       # X（旧Twitter）・ブラックスレート
        "insta": "#C026D3",   # Instagram・マゼンタ
        "threads": "#0E7490", # Threads・ティールシアン
        "tiktok": "#E11D48",  # TikTok・ローズレッド
        "ops": "#F0851A",     # AI活用・運用管理・オレンジ
        "ref": "#0F766E",     # 巻末資料・ティール
    },
    "cover": {
        "kicker": "AI SNS OPERATION COMPLETE COURSE",
        "title_lines": ["AI×SNS運用代行", "完全習得講座"],
        "tagline": "X／Instagram／Threads／TikTok",
        "tagline2": "投稿設計から分析・レポートまでを一冊で学ぶ、実務ノウハウ8割の教科書",
        "stripe_keys": ["base", "x", "insta", "threads", "tiktok", "ops"],
        "badges": [
            ("X", "X（旧Twitter）", "x"),
            ("INSTAGRAM", "Instagram", "insta"),
            ("THREADS", "Threads", "threads"),
            ("TIKTOK", "TikTok", "tiktok"),
        ],
        "structure_note": "全6部・16章／巻末資料つき　4大SNSの運用代行を一気に実務レベルへ引き上げる完全ガイド",
    },
    "intro_paragraphs": [
        "本書は、AIツールを使って**企業・個人事業主のSNSアカウントを預かり、運用を代行して報酬を得る**"
        "ための実務書です。「SNSに詳しくなる本」ではなく、「SNS運用代行の仕事を受注し、回せるようになる本」を"
        "目指して構成しました。そのため、内容の8割は現場で使えるノウハウ（手順・型・テンプレート・判断基準）にあてています。",
        "扱うプラットフォームは、運用代行の依頼がもっとも多い**X（旧Twitter）・Instagram・Threads・TikTok**の"
        "4つです。それぞれのアルゴリズムや投稿の型は異なりますが、AIを使った投稿制作・分析・レポーティングの"
        "土台は共通しています。プラットフォームごとの違いと、共通する運用の型の両方を身につけられる構成です。",
    ],
    "structure_rows": [
        ["第1部　基礎編", "SNS運用代行の全体像・案件獲得・単価設計・ヒアリング",
         "仕事の取り方と、お金の設計ができる"],
        ["第2部　X運用", "Xのアルゴリズム・投稿設計・伸びる投稿の型",
         "X単体での運用代行ができる"],
        ["第3部　Instagram運用", "フィード・リール・ストーリーズの使い分けと設計",
         "Instagram単体での運用代行ができる"],
        ["第4部　Threads運用", "Threadsの特性とテキスト中心の運用設計",
         "Threads単体での運用代行ができる"],
        ["第5部　TikTok運用", "TikTokのアルゴリズムとショート動画の型",
         "TikTok単体での運用代行ができる"],
        ["第6部　AI活用と実務運用", "AI制作フロー・分析レポート・炎上対応・30日ロードマップ",
         "複数アカウントを継続的に回せる"],
    ],
    "structure_widths_ratio": [0.24, 0.44, 0.32],
    "study_plan": [
        "**1周目**：第1部を読み、次に自分が最初に受注したいプラットフォームの部を1つ選んで読む。",
        "**2周目**：選んだプラットフォームで実際にテストアカウントを運用し、投稿を10本作ってみる。",
        "**3周目以降**：第6部のAI活用・分析・30日ロードマップに沿って、案件獲得と運用を同時に回す。"
        "他のプラットフォームは、案件が決まってから該当する部を読んで対応すればよい。",
    ],
}

if __name__ == "__main__":
    engine.configure(CONFIG)
    sys.exit(engine.main())
