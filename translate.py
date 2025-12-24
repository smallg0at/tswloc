import pandas as pd
from google.cloud import translate_v2 as translate
import html
import os
import csv
import re

# --- 配置区域 ---
GLOSSARY_FILE = "glossary.csv"  # 你的无头术语表文件

# 加载环境变量以使用 Google 凭据
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "C:\\Code\\tswloc\\lithe-hallway-473510-s6-cd50ed72e0d4.json"
)


def load_glossary(file_path):
    """加载无表头CSV术语表：第一列原文，第二列译文"""
    glossary = {}
    if not os.path.exists(file_path):
        print(f"⚠️ 未找到术语表文件: {file_path}，将跳过暴力替换。")
        return glossary

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                # 存入字典：{ "Power Handle": "功率手柄" }
                glossary[row[0].strip()] = row[1].strip()

    # 按长度倒序排序，防止短词破坏长词（如防止 'Train' 破坏 'Train Brake'）
    return dict(sorted(glossary.items(), key=lambda x: len(x[0]), reverse=True))

def apply_glossary(original_text, translated_text, glossary):
    """
    根据原文判定是否包含术语，若包含，则在译文中强制修正。
    """
    if not isinstance(translated_text, str) or not glossary:
        return translated_text

    for en_term, zh_term in glossary.items():
        # 1. 检查【原文】中是否包含该术语 (忽略大小写)
        if en_term.lower() in original_text.lower():
            # 2. 如果原文有这个词，我们需要在【译文】中找到 Google 可能翻错的结果并替换
            # 这里有个难点：我们不知道 Google 把这个词翻成了什么（可能翻成 A，也可能翻成 B）
            # 暴力策略：如果译文里已经没有英文原文了，我们可能需要更复杂的映射。

            # 策略 A：直接把译文中对应的部分换掉（如果译文保留了部分英文）
            pattern = re.compile(re.escape(en_term), re.IGNORECASE)
            if pattern.search(translated_text):
                translated_text = pattern.sub(zh_term, translated_text)
            else:
                # 如果你希望最暴力：如果原文只有这个词，直接返回术语表译文
                if original_text.strip().lower() == en_term.lower():
                    return zh_term

    # 额外修复占位符
    translated_text = translated_text.replace("{ ", "{").replace(" }", "}")
    return translated_text


def translate_tsw_csv(input_file, output_file, target_lang="zh-CN"):
    # 0. 加载本地术语表
    glossary = load_glossary(GLOSSARY_FILE)
    print(f"✅ 已加载术语词条: {len(glossary)} 条")

    # 1. 初始化客户端
    client = translate.Client()

    # 2. 读取 CSV
    print(f"正在加载: {input_file}")
    df = pd.read_csv(input_file)

    # 3. 提取唯一原文进行翻译
    # fix 可能存在的 NaN 问题
    df["source"] = df["source"].fillna("")
    unique_sources = df["source"].unique().tolist()
    print(f"检测到总行数: {len(df)}, 唯一待翻译词条数: {len(unique_sources)}")

    translated_map = {}
    batch_size = 50

    print(f"开始调用 Google API 翻译...")
    for i in range(0, len(unique_sources), batch_size):
        batch = unique_sources[i : i + batch_size]
        try:
            results = client.translate(batch, target_language=target_lang)

            for original, res in zip(batch, results):
                # 解码 HTML 实体
                translated_text = html.unescape(res["translatedText"])

                translated_text = apply_glossary(original, translated_text, glossary)

                translated_map[original] = translated_text

            print(
                f"进度: {min(i + batch_size, len(unique_sources))}/{len(unique_sources)}"
            )
        except Exception as e:
            print(f"翻译批次 {i} 失败: {e}")
            for text in batch:
                translated_map[text] = text

    # 4. 映射回 Translation 列
    print("正在匹配翻译结果...")
    df["Translation"] = df["source"].map(translated_map)

    # 5. 保存结果
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"🎉 翻译并修正完成！已保存至: {output_file}")


if __name__ == "__main__":
    # 配置
    file = "AABS_Class350_BTP.locres.csv"
    out_file = file.replace(".locres.csv", "_translated.csv")
    config = {
        "input_file": file,
        "output_file": out_file,
        "target_lang": "zh-CN",
    }

    translate_tsw_csv(**config)
