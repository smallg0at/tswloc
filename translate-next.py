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

GLOSSARY_FILE = "glossary.csv"
TARGET_LANG = "zh-CN"
FILE = "CrossCity_170Pack_Gameplay.locres.csv"


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
                text="""你是一个精通《模拟火车世界》(Train Sim World) 和英国铁路规程的专业翻译官。请将以下文本翻译成中文，需要使用专业铁路用语。除非原文包含，或部分重度缩写地名如DIRFT，避免使用括号。对于车次，使用如下格式：<车次号> <时间码（如有）> <始发站译名>至<终点站译名（均不包括英文名）>。站场、避让线、维护设施、货运站等的缩写（如FLT）需要进行翻译，地点名称不需要保留英文名称，站名中仅货运公司名称需要保留原文。Part X 翻译为第 X 部分。"""
            ),
        ],
    )

    result_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # print(chunk.text)
        result_text += chunk.text

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
        # add , between items to avoid issues
        batch_text = ",\n".join(batch)
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
        time.sleep(13)

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
