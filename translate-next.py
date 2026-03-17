import pandas as pd
from google.cloud import translate_v2 as translate
import html
import os
import csv
import re

import base64
import os
from google import genai
from google.genai import types
import json
import time

SYSTEM_ROLE = "你是一个精通《模拟火车世界》(Train Sim World) 和德国铁路规程与机车的专业翻译官。"

SYSTEM_RULES = [
    "将输入文本翻译成中文，使用专业铁路用语。",
    "除非原文包含，或部分重度缩写地名如 DIRFT，避免使用括号。",
    "对于车次，使用如下格式：<列车种别> (<车次号>) <始发站>—<终到站>",
    "列车种别不翻译。{ }包裹的内容为占位符，不要翻译但要保留花括号。",
    "站场、避让线、维护设施、货运站等的缩写（如 FLT）需要翻译。",
    "地点名称不保留英文名称；站名中仅货运公司名称保留原文。",
    "Part X 翻译为第 X 部分。",
    "不要添加解释、注释或额外字段。",
]

STATION_TRANSLATIONS = {
    "Stará Paka": "斯塔拉帕卡",
    "Bělá u Staré Paky": "斯塔拉帕卡附近的别拉",
    "Libštát": "利布什塔特",
    "Košťálov": "科什佳洛夫",
    "Nedvězí": "内德维济",
    "Semily": "塞米利",
    "Železný Brod": "热莱兹尼布罗德",
    "Líšný": "利什尼",
    "Malá Skála": "马拉斯卡拉",
    "Dolánky": "多兰基",
    "Turnov": "图尔诺夫",
    "Doubí u Turnova": "图尔诺夫附近的道比",
    "Sychrov": "锡赫罗夫",
    "Sedlejovice": "塞德莱约维采",
    "Hodkovice n. M.": "莫黑尔卡河畔霍德科维采",
    "Rychnov u Jabl. n.n.": "尼萨河畔亚布洛内茨附近的里赫诺夫",
    "Rádlo": "拉德洛",
    "Jeřmanice": "耶日马尼采",
    "Pilínkov": "皮林科夫",
    "Liberec": "利贝雷茨",
}


def build_system_instruction() -> str:
    rule_lines = "\n".join(f"{idx + 1}. {rule}" for idx, rule in enumerate(SYSTEM_RULES))
    station_lines = "\n".join(
        f"- {source}: {target}" for source, target in STATION_TRANSLATIONS.items()
    )
    return (
        f"{SYSTEM_ROLE}\n"
        f"任务要求：\n{rule_lines}\n"
        # "请在翻译时严格遵守以下站名固定译名：\n"
        # f"{station_lines}"
    )


SYSTEM_INSTRUCTION = build_system_instruction()

GLOSSARY_FILE = "glossary.csv"
TARGET_LANG = "zh-CN"
FILE = "CRG_DB_BR145_Expert_Gameplay.145pack.locres.csv"


def translate_gemini(input_text: str):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-flash-latest"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=input_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            properties={
                "output": genai.types.Schema(
                    type=genai.types.Type.ARRAY,
                    items=genai.types.Schema(
                        type=genai.types.Type.STRING,
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(
                text=SYSTEM_INSTRUCTION
            ),
        ],
    )

    result_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        try:
            result_text += chunk.text
        except Exception as e:
            print(f"Error processing chunk: {e}. Chunk content: {chunk}")
            input("Press Enter to continue...")

    # Process result_text to extract translations
    try:
        result_json = json.loads(result_text)
        translations = result_json.get("output", [])
        print(translations)
        return translations
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return []


def load_glossary(file_path):
    """Load Glossary: source,target"""
    glossary = {}
    if not os.path.exists(file_path):
        print(f"⚠️ Glossary Not found: {file_path}")
        return glossary

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                glossary[row[0].strip()] = row[1].strip()

    # Sort by length of source term, descending to match longer terms first
    return dict(sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True))


def apply_glossary(original_text, translated_text, glossary):
    """
    Apply glossary corrections to the translated text.
    """
    if not isinstance(translated_text, str) or not glossary:
        return translated_text

    for en_term, zh_term in glossary.items():
        if original_text.strip().lower() == en_term.lower():
            return zh_term

    # 额外修复占位符
    translated_text = translated_text.replace("{ ", "{").replace(" }", "}")
    return translated_text


def translate_tsw_csv(input_file, output_file, target_lang="zh-CN"):
    glossary = load_glossary(GLOSSARY_FILE)
    print(f"✅ Glossary Loaded: {len(glossary)} entries")

    print(f"Loading file: {input_file}")
    df = pd.read_csv(input_file)

    # fix nans caused by nones
    df["source"] = df["source"].fillna("None")

    unique_sources = df["source"].unique().tolist()
    print(f"Rows: {len(df)}, Unique entries to translate: {len(unique_sources)}")

    translated_map = {}
    batch_size = 100

    print(f"Starting Google API translation...")
    for i in range(0, len(unique_sources), batch_size):  # testing!
        batch = unique_sources[i : i + batch_size]
        print(f"Translating batch {i//batch_size +1}: {len(batch)} items...")
        batch_text = json.dumps({"input": batch}, ensure_ascii=False)
        result = translate_gemini(batch_text)
        # result is expected to be a list of translations matching batch order
        if isinstance(result, list) and len(result) == len(batch):
            for src, tgt in zip(batch, result):
                corrected = apply_glossary(src, tgt, glossary)
                translated_map[src] = corrected
        else:
            # fallback: assign empty translation (or keep original) and apply glossary if possible
            for src in batch:
                translated_map[src] = apply_glossary(src, "", glossary)
        if i == 0:
            if input("First batch done. Continue? (y/n)").lower() != "y":
                print("Translation aborted by user.")
                return
        # rpm=5, wait between batches
        print("Waiting to respect rate limits...")
        time.sleep(1)

    # 4. 映射回 Translation 列
    print("Mapping translation results...")
    df["target"] = df["source"].map(translated_map)

    # 5. 保存结果
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"🎉 Translation and corrections completed! Saved to: {output_file}")


if __name__ == "__main__":
    # 配置
    file = FILE
    out_file = file.replace(".locres.csv", "_translated.csv")
    config = {
        "input_file": file,
        "output_file": out_file,
        "target_lang": TARGET_LANG,
    }

    translate_tsw_csv(**config)
