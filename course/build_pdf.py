#!/usr/bin/env python3
"""「AIフリーランス業務完全習得講座」PDF ビルダー。

course/content/*.txt に書かれた独自記法のテキストを読み込み、
色分けされた学習教材PDFを生成する。実際の組版処理は course/engine.py。

    python course/build_pdf.py

出力: manuals/AIフリーランス業務完全習得講座.pdf
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import engine

CONFIG = {
    "title": "AIフリーランス業務完全習得講座",
    "subtitle": "ライティング／画像生成／動画生成でお金を稼ぐための実務書",
    "out_path": os.path.join(ROOT, "manuals", "AIフリーランス業務完全習得講座.pdf"),
    "content_dir": os.path.join(HERE, "content"),
    "org_line": "マイワーク AIスクール",
    "default_theme_key": "base",
    "study_plan_theme_key": "ops",
    "part_colors": {
        "base": "#2B5CE6",   # 基礎編・ブルー
        "write": "#0E9F6E",  # ライティング・グリーン
        "image": "#8B5CF6",  # 画像生成・パープル
        "video": "#E0245E",  # 動画生成・ピンクレッド
        "ops": "#F0851A",    # 実務運用・オレンジ
        "ref": "#0F766E",    # 巻末資料・ティール
    },
    "cover": {
        "kicker": "AI FREELANCE COMPLETE COURSE",
        "title_lines": ["AIフリーランス", "業務完全習得講座"],
        "tagline": "ライティング／画像生成／動画生成",
        "tagline2": "案件獲得から納品までを一冊で学ぶ、実務ノウハウ8割の教科書",
        "stripe_keys": ["base", "write", "image", "video", "ops"],
        "badges": [
            ("WRITING", "AIライティング", "write"),
            ("IMAGE", "AI画像生成", "image"),
            ("VIDEO", "AI動画生成", "video"),
        ],
        "structure_note": "全5部・22章／巻末資料つき　初心者から実務レベルまで最短で到達するための完全ガイド",
    },
    "intro_paragraphs": [
        "本書は、AIツールを使って**実際に仕事を受注し、納品し、報酬を得る**ための実務書です。"
        "「AIについて詳しくなる本」ではなく、「AIで稼げるようになる本」を目指して構成しました。"
        "そのため、内容の8割は現場で使えるノウハウ（手順・型・テンプレート・判断基準）にあてています。",
        "扱うジャンルは需要が大きく、かつ初心者でも参入しやすい**ライティング・画像生成・動画生成**の3つです。"
        "それぞれについて「基礎知識 → プロンプト設計 → 案件別の実務手順 → 品質管理と納品」という同じ流れで学べるようにしてあります。",
    ],
    "structure_rows": [
        ["第1部　基礎編", "AIフリーランスの全体像・案件獲得・単価設計・要件定義",
         "仕事の取り方と、お金の設計ができる"],
        ["第2部　ライティング", "AIライティングの基礎・プロンプト設計・SEO記事・品質管理",
         "記事案件を一人で完結できる"],
        ["第3部　画像生成", "画像生成の仕組み・プロンプト設計・案件別レシピ・権利",
         "バナー／サムネ／商品画像を作れる"],
        ["第4部　動画生成", "動画AIの基礎・ショート動画制作・台本と音声・編集と書き出し",
         "ショート動画を量産・納品できる"],
        ["第5部　実務運用", "効率化・トラブル対応・30日ロードマップ",
         "継続的に回る仕事の仕組みを作れる"],
    ],
    "study_plan": [
        "**1周目**：第1部→第2部と順に読み、各章末の「まとめ」とチェックリストだけで理解度を確認する。",
        "**2周目**：自分がやりたいジャンルの部（第2〜4部）を手を動かしながら再読し、成果物を3点作る。",
        "**3周目以降**：第5部の30日ロードマップに沿って、営業と制作を同時に回す。詰まったら該当章に戻る。",
    ],
}

if __name__ == "__main__":
    engine.configure(CONFIG)
    sys.exit(engine.main())
