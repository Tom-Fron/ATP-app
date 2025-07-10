import pandas as pd
import json
import random
import os
base_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(base_dir, "quiz_questions.xlsx")
template_file = os.path.join(base_dir, "template.html")
output_file = os.path.join(base_dir, "Netlify", "index.html")
audio_folder = os.path.join(base_dir, "tts_audio")
questions_json_path = os.path.join(base_dir, "Netlify", "questions.json")

# Excel読み込み
df = pd.read_excel(input_file)

questions_by_category = {}

def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

for _, row in df.iterrows():
    category = f"{safe_str(row['カテゴリ'])}\n{safe_str(row['カテゴリ(タイ語)'])}"
    question_text = f"{safe_str(row['問題文'])}\n{safe_str(row['問題文(タイ語)'])}"
    
    correct = []
    for i in range(1, 4):
        jp = safe_str(row.get(f"正答{i}"))
        th = safe_str(row.get(f"正答{i}(タイ語)"))
        if jp:
            correct.append({"jp": jp, "th": th})

    choice_jp_corrects = [c["jp"] for c in correct]
    choice_jp_wrongs = [safe_str(row[f"誤答{i}"]) for i in range(1, 4) if pd.notna(row[f"誤答{i}"])]
    choices = choice_jp_corrects + choice_jp_wrongs
    
    if pd.notna(row['解説']) or pd.notna(row['解説(タイ語)']):
        explanation = f"{safe_str(row['解説'])}\n{safe_str(row['解説(タイ語)'])}"
    else:
        explanation = ""

    if pd.notna(row['No.']):
        number = int(row['No.'])
    else:
        number = 0

    if pd.notna(row['カテゴリNo.']):
        categoryNo = int(row['カテゴリNo.'])
    else:
        categoryNo = 0

    number_str = str(number).zfill(2)
    categoryNo_str = str(categoryNo)

    q_obj = {
        "question": question_text,
        "correct": correct,
        "choices": choices,
        "explanation": explanation,
        "number": number_str,
        "category": safe_str(row['カテゴリ']),
        "categoryNo": categoryNo_str
    }
    questions_by_category.setdefault(category, []).append(q_obj)

for key in questions_by_category:
    random.shuffle(questions_by_category[key])

# JSON文字列化
questions_json = json.dumps(questions_by_category, ensure_ascii=False)

# JSのバッククオート文字や制御文字に備えてエスケープ
questions_json_escaped = questions_json.replace('\\', '\\\\').replace('`', '\\`').replace('\n', '\\n')

# テンプレート読み込み
with open(template_file, "r", encoding="utf-8") as f:
    template = f.read()

# JSONをテンプレートに差し込む
output_html = (
    template
    .replace("{questions_json}", questions_json_escaped)
    .replace("{audio_json}", "{}")
)

# 出力
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_html)

print(f"✅ HTMLファイルを生成しました: {output_file}")

with open(questions_json_path, "w", encoding="utf-8") as f:
    json.dump(questions_by_category, f, ensure_ascii=False, indent=2)

print("✅ questions.json を出力しました。")
