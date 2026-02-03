import pandas as pd
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
from gtts import gTTS

input_file = "quiz_questions.xlsx"
output_dir = os.path.join(base_dir, "tts_audio")
os.makedirs(output_dir, exist_ok=True)

df = pd.read_excel(input_file)

# Debug: 列名一覧表示
print("列名:", df.columns.tolist())

audio_cols = ["正答音声1", "正答音声2", "正答音声3"]

for idx, row in df.iterrows():
    category_no = str(row["カテゴリNo."]).strip()
    qnum_raw = row["No."]
    try:
        qnum = str(int(qnum_raw)).zfill(2)
    except:
        print(f"⚠️ 無効なNo.値: {qnum_raw}")
        continue

    for i in range(1, 4):
        col_name = audio_cols[i-1]
        text = row.get(col_name)

        if pd.isna(text) or not str(text).strip():
            continue

        text_str = str(text).strip()
        text_str = text_str.replace("_", "、、、。。。。。。。。。").replace("＿", "、、、。。。。。。。。。")
        filename = f"{category_no}-{qnum}-{i}.mp3"
        filepath = os.path.join(output_dir, filename)

        try:
            tts = gTTS(text=text_str, lang='ja')
            tts.save(filepath)
            print(f"✅ 作成完了: {filename}")
        except Exception as e:
            print(f"⚠️ エラー: {filename} の生成に失敗しました: {e}")
