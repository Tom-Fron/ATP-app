import pandas as pd
import os
import re
from gtts import gTTS

input_file = "quiz_questions.xlsx"
output_dir = "tts_audio"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_excel(input_file)

# Debug: 列名一覧表示
print("列名:", df.columns.tolist())

for idx, row in df.iterrows():
    category_no = str(row["カテゴリNo."]).strip()
    qnum_raw = row["No."]
    try:
        qnum = str(int(qnum_raw)).zfill(2)
    except:
        print(f"⚠️ 無効なNo.値: {qnum_raw}")
        continue

    for i in range(1, 4):
        if category_no == "1" and qnum == "09" and i in [2, 3]:
            col_name = "Unnamed: 15" if i == 2 else "Unnamed: 16"
            text = row.get(col_name)
            print(f"🔍 {category_no}-{qnum}-{i} text from {col_name}: {text}")
        else:
            col_name = f"正答{i}"
            text = row.get(col_name)

        if pd.isna(text) or not str(text).strip():
            continue

        text_str = str(text).strip()
        text_str = text_str.replace("_", " \n\n\n。。。、、、 ").replace("＿", " \n\n\n。。。、、、 ")
        text_str = re.sub(r"[（(][^）)]+[）)]", "", text_str)
        text_str = re.sub(r"[\u0E00-\u0E7F]+", "", text_str)

        text_str = text_str.strip()
        if not text_str:
            continue

        filename = f"{category_no}-{qnum}-{i}.mp3"
        filepath = os.path.join(output_dir, filename)

        try:
            tts = gTTS(text=text_str, lang='ja')
            tts.save(filepath)
            print(f"✅ 作成完了: {filename}")
        except Exception as e:
            print(f"⚠️ エラー: {filename} の生成に失敗しました: {e}")
