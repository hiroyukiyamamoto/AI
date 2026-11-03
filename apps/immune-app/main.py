import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Immune Cell Learning App",
    description="免疫細胞について楽しく学べるインタラクティブWebアプリ",
    version="1.0.0"
)

# Static files setup
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Immune Cell Learning API is running!"}

# Data models & Endpoint Data
CELLS_DATA = [
    {
        "id": "macrophage",
        "name": "マクロファージ",
        "englishName": "Macrophage",
        "category": "innate",
        "badge": "自然免疫・食細胞",
        "catchphrase": "何でも貪食する大食いファイター",
        "icon": "🛡️",
        "color": "#e11d48", # rose-600
        "bgGradient": "from-rose-500 to-red-600",
        "description": "体内に侵入した細菌やウイルス、死んだ細胞を食べて分解（貪食）します。分解した病原体の情報を樹状細胞やT細胞に伝える「抗原提示」という重要な役割も担っています。",
        "features": [
            "強い貪食能力（病原体や異物を丸のみ）",
            "抗原提示能力（敵の情報を仲間に伝える）",
            "サイトカイン（情報伝達物質）を放出して炎症を起こす"
        ],
        "stats": {"攻撃力": 80, "貪食力": 95, "情報伝達": 70, "耐久性": 85}
    },
    {
        "id": "neutrophil",
        "name": "好中球",
        "englishName": "Neutrophil",
        "category": "innate",
        "badge": "自然免疫・先陣部隊",
        "catchphrase": "真っ先に駆けつける最前線突撃隊長",
        "icon": "⚔️",
        "color": "#ea580c", # orange-600
        "bgGradient": "from-amber-500 to-orange-600",
        "description": "白血球の中で最も数が多く（約50〜70%）、病原体が侵入すると真っ先に現場へ急行して細菌を貪食します。寿命は数日と短く、戦い終えると「膿（うみ）」となります。",
        "features": [
            "白血球中最大の存在数",
            "血管壁をすり抜けて最速で感染現場へ駆けつける",
            "NETs（細胞外トラップ）を放出して細菌を捕獲"
        ],
        "stats": {"攻撃力": 85, "スピード": 100, "貪食力": 90, "寿命": 30}
    },
    {
        "id": "dendritic",
        "name": "樹状細胞",
        "englishName": "Dendritic Cell",
        "category": "bridge",
        "badge": "自然・獲得免疫の架け橋",
        "catchphrase": "免疫系の最重要情報メッセンジャー",
        "icon": "📡",
        "color": "#0284c7", # sky-600
        "bgGradient": "from-sky-500 to-blue-600",
        "description": "皮膚や粘膜など体表近くに常駐し、敵を捕らえるとリンパ節へ移動します。敵の断片（抗原）をヘルパーT細胞に見せて「こんな敵が来た！」と警告し、獲得免疫を発動させます。",
        "features": [
            "最強の抗原提示能力",
            "リンパ節へ移動してT細胞を活性化",
            "敵のタイプに応じた適切な免疫反応を誘導"
        ],
        "stats": {"情報伝達": 100, "偵察力": 95, "攻撃力": 30, "重要度": 100}
    },
    {
        "id": "helper_t",
        "name": "ヘルパーT細胞",
        "englishName": "Helper T Cell",
        "category": "adaptive",
        "badge": "獲得免疫・総司令官",
        "catchphrase": "全免疫部隊を指揮する司令塔",
        "icon": "👑",
        "color": "#7c3aed", # violet-600
        "bgGradient": "from-indigo-500 to-purple-600",
        "description": "樹状細胞から提示された抗原情報を受け取り、サイトカイン（化学物質）を放出してB細胞（抗体製造）やキラーT細胞（攻撃指示）に最適な作戦を指示します。",
        "features": [
            "免疫応答全体の方向性を決定（Th1, Th2など）",
            "B細胞に抗体産生を命令",
            "マクロファージやキラーT細胞の活性化"
        ],
        "stats": {"指揮力": 100, "情報分析": 95, "攻撃力": 20, "統率力": 95}
    },
    {
        "id": "killer_t",
        "name": "キラーT細胞",
        "englishName": "Cytotoxic T Cell",
        "category": "adaptive",
        "badge": "獲得免疫・細胞傷害性T細胞",
        "catchphrase": "感染細胞を精密に撃破する暗殺者",
        "icon": "🎯",
        "color": "#dc2626", # red-600
        "bgGradient": "from-red-600 to-rose-700",
        "description": "ウイルスに感染した自身の細胞や、がん化した細胞を発見し、パフォーリンやグランザイムなどの穿孔性毒素を放出して細胞ごと破壊し、感染拡大を防ぎます。",
        "features": [
            "感染した自体細胞の特定撃破",
            "がん細胞の認識と攻撃",
            "メモリーT細胞となって次回侵入に備える"
        ],
        "stats": {"攻撃力": 95, "精密性": 90, "耐久性": 75, "ターゲット識別": 95}
    },
    {
        "id": "b_cell",
        "name": "B細胞",
        "englishName": "B Lymphocyte",
        "category": "adaptive",
        "badge": "獲得免疫・抗体製造工場",
        "catchphrase": "精密誘導ミサイル『抗体』の量産工場",
        "icon": "🏹",
        "color": "#2563eb", # blue-600
        "bgGradient": "from-blue-600 to-cyan-600",
        "description": "ヘルパーT細胞の刺激を受けると「形質細胞」に変身（分化）し、病原体にピッタリ合体する「抗体（ミサイル）」を毎秒数千個生産して、毒素やウイルスを無力化（中和）します。",
        "features": [
            "特異的抗体（IgG, IgA, IgE等）の大量分泌",
            "病原体の中和・凝集・補体活性化",
            "メモリーB細胞となり長期間記憶"
        ],
        "stats": {"遠距離攻撃": 100, "生産力": 95, "直接戦闘": 20, "記憶力": 90}
    },
    {
        "id": "nk_cell",
        "name": "NK細胞",
        "englishName": "Natural Killer Cell",
        "category": "innate",
        "badge": "自然免疫・単独巡回者",
        "catchphrase": "事前指令なしで異物を見抜く一匹狼",
        "icon": "⚡",
        "color": "#059669", # emerald-600
        "bgGradient": "from-emerald-500 to-teal-600",
        "description": "他の細胞からの指令を待つことなく、体中を常時パトロール。正常な細胞の標識（MHC class I）が減っている変異細胞（がん細胞やウイルス感染細胞）を見つけると即座に攻撃します。",
        "features": [
            "指令不要の自律的攻撃判断",
            "がん細胞の初期排除（がんサベイランス）",
            "笑いやストレス軽減で活性が上がる"
        ],
        "stats": {"攻撃力": 90, "単独行動": 100, "即応性": 95, "監視力": 85}
    },
    {
        "id": "treg",
        "name": "制御性T細胞",
        "englishName": "Regulatory T Cell (Treg)",
        "category": "adaptive",
        "badge": "獲得免疫・ブレーキ役",
        "catchphrase": "免疫の暴走を抑える平和の守護神",
        "icon": "🕊️",
        "color": "#16a34a", # green-600
        "bgGradient": "from-green-500 to-emerald-700",
        "description": "病原体を撃退した後に、他のT細胞やB細胞の働きを抑えて免疫反応を終息させます。自分自身の体を攻撃してしまう「自己免疫疾患」や「アレルギー」を防ぐ極めて大切な細胞です。",
        "features": [
            "過剰な免疫反応の抑制・鎮静化",
            "自己免疫疾患（リウマチや1型糖尿病など）の予防",
            "免疫バランスの維持"
        ],
        "stats": {"抑制力": 100, "安全性": 95, "制御力": 95, "攻撃力": 0}
    },
    {
        "id": "mast_cell",
        "name": "肥満細胞",
        "englishName": "Mast Cell",
        "category": "innate",
        "badge": "自然免疫・アレルギー発動",
        "catchphrase": "ヒスタミン爆薬を抱えた超敏感センサー",
        "icon": "💥",
        "color": "#d97706", # amber-600
        "bgGradient": "from-amber-500 to-yellow-600",
        "description": "粘膜や皮膚に存在し、IgE抗体とアレルゲン（花粉など）が結合すると、ヒスタミン等の化学物質を一気に放出し、くしゃみ・鼻水・血管拡張を引き起こして異物を排出しようとします。",
        "features": [
            "ヒスタミンやロイコトリエンの放出",
            "花粉症やアナフィラキシーに関与",
            "寄生虫排除の本来の役割"
        ],
        "stats": {"感受性": 95, "炎症誘発": 90, "警報機能": 90, "攻撃力": 40}
    }
]

SIMULATION_SCENARIOS = [
    {
        "id": "flu_invasion",
        "title": "Stage 1: インフルエンザウイルスの気道侵入！",
        "difficulty": "初級",
        "description": "気道上皮細胞にインフルエンザウイルスが侵入し、細胞内で爆発的に増殖を始めています！正しい手順で免疫細胞を発動させ、感染拡大を防いで体調を回復させましょう。",
        "steps": [
            {
                "stepNumber": 1,
                "question": "【ステップ1】ウイルス侵入直後、真っ先に現場へ駆けつけてウイルス感染細胞を独自に警戒・攻撃する自然免疫細胞はどれ？",
                "options": [
                    {"id": "nk_cell", "text": "NK細胞（Natural Killer）", "correct": True, "reason": "正解！NK細胞は指示を待たずに感染細胞の変化を察知し、即座に攻撃を開始します。"},
                    {"id": "b_cell", "text": "B細胞", "correct": False, "reason": "B細胞は獲得免疫の細胞で、抗体を作るにはヘルパーT細胞の指令と時間（数日）が必要です。"},
                    {"id": "treg", "text": "制御性T細胞（Treg）", "correct": False, "reason": "Tregは免疫を抑えるブレーキ役です。侵入直後に発動するとウイルスが増殖してしまいます！"}
                ]
            },
            {
                "stepNumber": 2,
                "question": "【ステップ2】病原体を貪食し、その抗原情報をリンパ節へ持ち込んで獲得免疫に受け渡す「司令部への伝令役」は？",
                "options": [
                    {"id": "dendritic", "text": "樹状細胞", "correct": True, "reason": "正解！樹状細胞は抗原を取り込んでリンパ節へ移動し、T細胞に強力に抗原提示します。"},
                    {"id": "neutrophil", "text": "好中球", "correct": False, "reason": "好中球は貪食専門の突撃隊員で、抗原提示をして獲得免疫を起動する能力は低いです。"},
                    {"id": "mast_cell", "text": "肥満細胞", "correct": False, "reason": "肥満細胞はヒスタミンを出してアレルギー反応を起こす細胞です。"}
                ]
            },
            {
                "stepNumber": 3,
                "question": "【ステップ3】すでにウイルスに感染して『ウイルス増殖工場』になってしまった体自身の細胞を狙い撃ちで破壊する細胞は？",
                "options": [
                    {"id": "killer_t", "text": "キラーT細胞", "correct": True, "reason": "正解！キラーT細胞（CD8+ T細胞）はウイルス感染細胞を認識し、直接破壊して感染の連鎖を断ち切ります。"},
                    {"id": "b_cell", "text": "B細胞", "correct": False, "reason": "B細胞が作る抗体は細胞の『外』にいるウイルスには効きますが、すでに『細胞の中』に入ったウイルスには届きません。"},
                    {"id": "macrophage", "text": "マクロファージ", "correct": False, "reason": "マクロファージも貪食しますが、感染細胞を特異的にピンポイント破壊するのはキラーT細胞が得意です。"}
                ]
            },
            {
                "stepNumber": 4,
                "question": "【ステップ4】ウイルスが全滅した後、過剰な炎症反応が続いて自分の肺組織を傷つけないように免疫を鎮圧する細胞は？",
                "options": [
                    {"id": "treg", "text": "制御性T細胞（Treg）", "correct": True, "reason": "正解！Tregが免疫応答にブレーキをかけることで、戦いが終わった後の組織の回復が始まります。"},
                    {"id": "helper_t", "text": "ヘルパーT細胞", "correct": False, "reason": "ヘルパーT細胞は免疫を刺激・活性化する方向へ働きます。"},
                    {"id": "neutrophil", "text": "好中球", "correct": False, "reason": "好中球は自爆して膿になるため、沈静化の役割はありません。"}
                ]
            }
        ]
    },
    {
        "id": "staph_infection",
        "title": "Stage 2: すり傷からの黄色ブドウ球菌（細菌）侵入！",
        "difficulty": "中級",
        "description": "転んでできた皮膚の擦り傷から、黄色ブドウ球菌が大量に進入！傷口が赤く腫れあがっています。細菌に対する最適な防御陣形を構築してください。",
        "steps": [
            {
                "stepNumber": 1,
                "question": "【ステップ1】血管をすり抜けて傷口へ一番乗りし、爆発的な数で細菌を貪食して食い止める白血球の主力を選べ！",
                "options": [
                    {"id": "neutrophil", "text": "好中球", "correct": True, "reason": "正解！血液中の白血球の半数以上を占める好中球が最速で駆けつけ、細菌をバクバク食べて死闘を繰り広げます。"},
                    {"id": "nk_cell", "text": "NK細胞", "correct": False, "reason": "NK細胞はウイルス感染細胞やがん細胞の監視が得意で、細菌の貪食処理は得意ではありません。"},
                    {"id": "b_cell", "text": "B細胞", "correct": False, "reason": "B細胞は初感染の細菌に対してすぐに抗体を出せるわけではありません。"}
                ]
            },
            {
                "stepNumber": 2,
                "question": "【ステップ2】細菌を不活性化し、マクロファージや好中球が食べやすくする（オプソニン化）ためにB細胞が作る武器は？",
                "options": [
                    {"id": "antibody", "text": "抗体（Immunoglobulin）", "correct": True, "reason": "正解！抗体が細菌の表面に付着すると、補体を活性化させたり食細胞が捕まえやすくなります（オプソニン効果）。"},
                    {"id": "histamine", "text": "ヒスタミン", "correct": False, "reason": "ヒスタミンは血管を広げてかゆみや腫れを起こす化学物質です。"},
                    {"id": "perforin", "text": "パフォーリン", "correct": False, "reason": "パフォーリンはキラーT細胞やNK細胞が敵の膜に穴を開けるタンパク質です。"}
                ]
            }
        ]
    }
]

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "白血球の中で最も数が多く、感染が起きると真っ先に現場に駆けつける自然免疫の細胞はどれ？",
        "options": ["マクロファージ", "好中球", "ヘルパーT細胞", "B細胞"],
        "answerIndex": 1,
        "explanation": "好中球は血液中の白血球の約50〜70%を占め、感染初期に最速で現場に急行して細菌などを貪食します。"
    },
    {
        "id": 2,
        "question": "病原体を食べて分解し、その断片（抗原）をT細胞に見せて指示を仰ぐ『抗原提示』を専門とする最強の細胞は？",
        "options": ["NK細胞", "赤血球", "樹状細胞", "血小板"],
        "answerIndex": 2,
        "explanation": "樹状細胞は体表や粘膜で抗原をキャッチすると、リンパ節へ移動してT細胞に強力な抗原提示を行います。"
    },
    {
        "id": 3,
        "question": "体内でウイルスに感染してしまった『自分自身の細胞』を直接認識して破壊する細胞はどれ？",
        "options": ["キラーT細胞", "B細胞", "肥満細胞", "赤血球"],
        "answerIndex": 0,
        "explanation": "キラーT細胞（CD8+ T細胞）はウイルス感染細胞やがん細胞の表面の異常分子を認識し、直接毒素を放出して破壊します。"
    },
    {
        "id": 4,
        "question": "B細胞が活性化して『形質細胞』になったときに大量に放出する、病原体を取り囲んで無力化するミサイルのような物質は？",
        "options": ["サイトカイン", "抗体（免疫グロブリン）", "ヒスタミン", "ヘモグロビン"],
        "answerIndex": 1,
        "explanation": "B細胞は抗体（Antibody）を生産し、病原体に特異的に結合して中和したり貪食を助けたりします。"
    },
    {
        "id": 5,
        "question": "他の細胞からの指示を待たずに、単独で体内を巡回して『がん細胞』や『感染細胞』を発見・攻撃する自然免疫細胞は？",
        "options": ["NK細胞（ナチュラルキラー細胞）", "制御性T細胞", "好塩基球", "ヘルパーT細胞"],
        "answerIndex": 0,
        "explanation": "NK細胞は名前の通り『生まれつきの殺し屋』で、事前学習なしで異常細胞を検出して迅速に攻撃します。"
    },
    {
        "id": 6,
        "question": "病原体が全滅した後に、免疫部隊の暴走を抑えてアレルギーや自己免疫疾患を防ぐ『ブレーキ役』の細胞はどれ？",
        "options": ["マクロファージ", "好中球", "制御性T細胞（Treg）", "ヘルパーT細胞"],
        "answerIndex": 2,
        "explanation": "制御性T細胞（Treg）は過剰な免疫応答を抑制し、自身の正常な組織が攻撃されないよう守る極めて重要な細胞です。"
    },
    {
        "id": 7,
        "question": "花粉症などのアレルギー反応において、IgE抗体と反応して『ヒスタミン』を放出し、くしゃみや鼻水を引き起こす細胞は？",
        "options": ["肥満細胞（マスト細胞）", "キラーT細胞", "樹状細胞", "NK細胞"],
        "answerIndex": 0,
        "explanation": "肥満細胞の表面にあるIgE抗体に花粉などのアレルゲンが結合すると、細胞内のヒスタミンが放出されてアレルギー症状が起きます。"
    },
    {
        "id": 8,
        "question": "一度侵入した病原体の特徴を記憶し、2回目の侵入時に超スピードで抗体を大量生産できるように準備している細胞は？",
        "options": ["好中球", "メモリーB細胞 / メモリーT細胞", "赤血球", "血小板"],
        "answerIndex": 1,
        "explanation": "獲得免疫の大きな特徴は『免疫記憶』です。メモリー細胞が存在するため、ワクチン接種や再感染時に迅速に防御できます。"
    },
    {
        "id": 9,
        "question": "笑うことで活性化が高まり、逆に過度なストレスで働きが低下することが知られている免疫細胞はどれ？",
        "options": ["NK細胞", "好中球", "赤血球", "血小板"],
        "answerIndex": 0,
        "explanation": "笑うと間脳に刺激が伝わり、自律神経や善玉ペプチドを通じてNK細胞の活性が上がることが研究で分かっています。"
    },
    {
        "id": 10,
        "question": "『自然免疫』と『獲得免疫』の違いとして正しいものはどれ？",
        "options": [
            "自然免疫は特定の敵専用に作られるが、届くまでに数日かかる",
            "自然免疫は生まれつき備わった即効性の防衛で、獲得免疫は敵を学習してピンポイントで攻撃する",
            "獲得免疫は誰でも生まれつき100%完璧に持っている",
            "自然免疫にはT細胞とB細胞が含まれる"
        ],
        "answerIndex": 1,
        "explanation": "自然免疫（好中球・マクロファージ・NK等）は即座に広範囲の異物に対応し、獲得免疫（T細胞・B細胞）は敵の情報を学習して精密攻撃を行います。"
    }
]

@app.get("/api/cells")
async def get_cells():
    return {"status": "success", "cells": CELLS_DATA}

@app.get("/api/cells/{cell_id}")
async def get_cell_detail(cell_id: str):
    cell = next((c for c in CELLS_DATA if c["id"] == cell_id), None)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    return {"status": "success", "cell": cell}

@app.get("/api/scenarios")
async def get_scenarios():
    return {"status": "success", "scenarios": SIMULATION_SCENARIOS}

@app.get("/api/quiz")
async def get_quiz():
    return {"status": "success", "questions": QUIZ_QUESTIONS}
