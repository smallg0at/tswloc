GLOSSARY_FILE = "glossary.csv"
TARGET_LANG = "zh-CN"
FILE = "GJL_Gameplay_translated.csv"

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
import argparse

SYSTEM_ROLE = "你是一个精通《模拟火车世界》(Train Sim World) 和英国铁路规程与机车的专业翻译官。"

SYSTEM_RULES = [
    "将输入文本翻译成中文，使用专业铁路用语。",
    "除非原文包含，或部分重度缩写地名如 DIRFT，避免使用括号。",
    "对于车次，使用如下格式：<车次号> <始发站>至<终到站>。如果原文只包含四位车次号则按原样翻译。",
    "{ }包裹的内容为占位符，不要翻译但要保留花括号。",
    "站场、避让线、维护设施、货运站等的缩写（如 FLT）需要翻译。",
    "地点名称不保留英文名称；站名中仅货运公司名称保留原文。",
    "Part X 翻译为第 X 部分。",
    "不要添加解释、注释或额外字段。",
]

STATION_TRANSLATIONS = {
    "Gravesend": "格雷夫森德",
    "Hoo Junction": "胡交汇站",
    "Higham": "海厄姆",
    "Strood": "斯特鲁德",
    "Rochester": "罗切斯特",
    "Chatham": "查塔姆",
    "Gillingham": "吉灵厄姆",
    "Gillingham Depot": "吉灵厄姆车辆段",
    "Rainham": "雷纳姆",
}


def build_system_instruction() -> str:
    rule_lines = "\n".join(f"{idx + 1}. {rule}" for idx, rule in enumerate(SYSTEM_RULES))
    station_lines = "\n".join(
        f"- {source}: {target}" for source, target in STATION_TRANSLATIONS.items()
    )
    return (
        f"{SYSTEM_ROLE}\n"
        f"任务要求：\n{rule_lines}\n"
    )


SYSTEM_INSTRUCTION = build_system_instruction()


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

    return dict(sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True))


def apply_glossary(original_text, translated_text, glossary):
    if not isinstance(translated_text, str) or not glossary:
        return translated_text

    for en_term, zh_term in glossary.items():
        if original_text.strip().lower() == en_term.lower():
            return zh_term

    translated_text = translated_text.replace("{ ", "{").replace(" }", "}")
    return translated_text


def translate_tsw_csv(input_file, output_file, target_lang="zh-CN", auto_continue=False):
    glossary = load_glossary(GLOSSARY_FILE)
    print(f"✅ Glossary Loaded: {len(glossary)} entries")

    print(f"Loading file: {input_file}")
    df = pd.read_csv(input_file)

    # Ensure expected columns exist
    if "source" not in df.columns:
        raise ValueError("CSV must contain a 'source' column")

    # Normalize target column (if missing, create it)
    if "target" not in df.columns:
        df["target"] = ""

    # Fill NaN in source to avoid issues
    df["source"] = df["source"].fillna("")

    # Only translate rows where the third column (target) is exactly 'TBT'
    mask = df["target"].astype(str).str.strip() == "TBT"
    to_translate = df.loc[mask, "source"].unique().tolist()
    print(f"Rows: {len(df)}, Rows to translate (TBT): {len(to_translate)}")

    if not to_translate:
        print("No rows marked 'TBT' to translate. Writing original file unchanged.")
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        return

    translated_map = {}
    batch_size = 100

    print(f"Starting Gemini API translation for TBT rows...")
    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i : i + batch_size]
        print(f"Translating batch {i//batch_size +1}: {len(batch)} items...")
        batch_text = json.dumps({"input": batch}, ensure_ascii=False)
        result = translate_gemini(batch_text)
        if isinstance(result, list) and len(result) == len(batch):
            for src, tgt in zip(batch, result):
                corrected = apply_glossary(src, tgt, glossary)
                translated_map[src] = corrected
        else:
            for src in batch:
                translated_map[src] = apply_glossary(src, "", glossary)
        if i == 0 and not auto_continue:
            if input("First batch done. Continue? (y/n)").lower() != "y":
                print("Translation aborted by user.")
                return
        print("Waiting to respect rate limits...")
        time.sleep(1)

    # Map back only for masked rows
    df.loc[mask, "target"] = df.loc[mask, "source"].map(translated_map)

    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"🎉 Translation completed! Saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", "-y", action="store_true", help="Auto continue after first batch")
    args = parser.parse_args()

    auto_continue = args.yes or os.environ.get("AUTO_CONTINUE", "0") == "1"

    file = os.path.join("csv", FILE)
    out_file = file.replace(".locres.csv", "_tbt_translated.csv")
    config = {
        "input_file": file,
        "output_file": out_file,
        "target_lang": TARGET_LANG,
        "auto_continue": auto_continue,
    }

    translate_tsw_csv(**config)
