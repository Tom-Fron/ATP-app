import pandas as pd
import json
import random
import base64
import os

input_file = "quiz_questions.xlsx"
template_file = "template.html"
output_file = "日本の生活.html"
audio_folder = "tts_audio"

# Excel読み込み
df = pd.read_excel(input_file)

questions_by_category = {}

for _, row in df.iterrows():
    category = f"{row['カテゴリ']}\n{row['カテゴリ(タイ語)']}"
    question_text = f"{row['問題文']}\n{row['問題文(タイ語)']}"
    correct = [str(row[f"正答{i}"]).strip() for i in range(1, 4) if pd.notna(row[f"正答{i}"])]
    choices = correct + [str(row[f"誤答{i}"]).strip() for i in range(1, 4) if pd.notna(row[f"誤答{i}"])]
    random.shuffle(choices)
    explanation = None
    if pd.notna(row['解説']) or pd.notna(row['解説(タイ語)']):
        explanation = f"{row['解説']}\n{row['解説(タイ語)']}"
    number = str(row['No.']).strip()
    categoryNo = str(row['カテゴリNo.']).strip()  # ここを追加
    q_obj = {
        "question": question_text,
        "correct": correct,
        "choices": choices,
        "explanation": explanation,
        "number": number,
        "category": row['カテゴリ'],
        "categoryNo": categoryNo  # ここも追加
    }
    questions_by_category.setdefault(category, []).append(q_obj)

for key in questions_by_category:
    random.shuffle(questions_by_category[key])

# 音声データBase64埋め込み
audio_data = {}
for filename in os.listdir(audio_folder):
    if filename.endswith(".mp3"):
        filepath = os.path.join(audio_folder, filename)
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            audio_data[filename] = f"data:audio/mp3;base64,{encoded}"

# JSON文字列化
questions_json = json.dumps(questions_by_category, ensure_ascii=False)
audio_json = json.dumps(audio_data, ensure_ascii=False)

# テンプレート読み込み
with open(template_file, "r", encoding="utf-8") as f:
    template = f.read()

# JSONをテンプレートに差し込む
output_html = template.replace("{questions_json}", questions_json).replace("{audio_json}", audio_json)

# 出力
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_html)

print(f"✅ HTMLファイルを生成しました: {output_file}")
