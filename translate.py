import pandas as pd
from google.cloud import translate_v2 as translate
import html
import os
import csv
import re

GLOSSARY_FILE = "glossary.csv"
TARGET_LANG = "zh-CN"
FILE = "AABS_Class350_BTP.locres.csv"

# Load Google Credential JSON, must change. DO NOT INCLUDE YOUR CREDENTIAL FILE IN PUBLIC REPO!
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "C:\\Code\\tswloc\\lithe-hallway-473510-s6-cd50ed72e0d4.json"
)


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
        if en_term.lower() in original_text.lower():
            pattern = re.compile(re.escape(en_term), re.IGNORECASE)
            if pattern.search(translated_text):
                translated_text = pattern.sub(zh_term, translated_text)
            else:
                if original_text.strip().lower() == en_term.lower():
                    return zh_term

    # 额外修复占位符
    translated_text = translated_text.replace("{ ", "{").replace(" }", "}")
    return translated_text


def translate_tsw_csv(input_file, output_file, target_lang="zh-CN"):
    glossary = load_glossary(GLOSSARY_FILE)
    print(f"✅ Glossary Loaded: {len(glossary)} entries")

    client = translate.Client()

    print(f"Loading file: {input_file}")
    df = pd.read_csv(input_file)

    # fix nans caused by nones
    df["source"] = df["source"].fillna("None")

    unique_sources = df["source"].unique().tolist()
    print(f"Rows: {len(df)}, Unique entries to translate: {len(unique_sources)}")

    translated_map = {}
    batch_size = 50

    print(f"Starting Google API translation...")
    for i in range(0, len(unique_sources), batch_size):
        batch = unique_sources[i : i + batch_size]
        try:
            results = client.translate(batch, target_language=target_lang)

            for original, res in zip(batch, results):
                translated_text = html.unescape(res["translatedText"])
                translated_text = apply_glossary(original, translated_text, glossary)
                translated_map[original] = translated_text

            print(
                f"Progress: {min(i + batch_size, len(unique_sources))}/{len(unique_sources)}"
            )
        except Exception as e:
            print(f"Translation batch {i} failed: {e}")
            for text in batch:
                translated_map[text] = text

    # 4. 映射回 Translation 列
    print("Mapping translation results...")
    df["Translation"] = df["source"].map(translated_map)

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
