import pandas as pd
import json
import random
import base64
import os

input_file = "quiz_questions.xlsx"
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
    number = str(row.iloc[0]).strip()  # A列（管理番号）
    q_obj = {
        "question": question_text,
        "correct": correct,
        "choices": choices,
        "explanation": explanation,
        "number": number,
        "category": row['カテゴリ']
    }
    questions_by_category.setdefault(category, []).append(q_obj)

for key in questions_by_category:
    random.shuffle(questions_by_category[key])

# 音声データ埋め込み（Base64変換）
audio_data = {}
for filename in os.listdir(audio_folder):
    if filename.endswith(".mp3"):
        filepath = os.path.join(audio_folder, filename)
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            audio_data[filename] = f"data:audio/mp3;base64,{encoded}"

questions_json = json.dumps(questions_by_category, ensure_ascii=False)
audio_json = json.dumps(audio_data, ensure_ascii=False)

html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>日本の生活(仮)</title>
  <style>
    body {{{{ font-family: sans-serif; background: #FFEFD5; text-align: center; padding: 10px 5px; }}}}
    .category-btn, #next, #restart {{{{
      padding: 14px 28px;
      font-size: 1.3em;
      margin: 10px auto;
      width: 90vw;
      max-width: 300px;
      background-color: orange;
      color: white;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      white-space: pre-line;
      display: block;
      box-sizing: border-box;
    }}}}
    .choice {{{{
      display: block;
      margin: 8px auto;
      padding: 14px 16px;
      font-size: 1.2em;
      max-width: 90vw;
      background-color: #ADD8E6;
      border-radius: 12px;
      position: relative;
      cursor: pointer;
      white-space: pre-wrap;
      text-align: left;
      word-break: break-word;
      box-sizing: border-box;
      text-indent: 0;
    }}}}
    .chosen {{{{ background-color: #87b4cc; }}}}
    .disabled {{{{ pointer-events: none; }}}}
    .mark {{{{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 2em;
      font-weight: bold;
      color: red;
      user-select: none;
      pointer-events: none;
    }}}}
    .speaker-icon {{{{
      cursor: pointer;
      font-size: 1.5em;
      color: #444;
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      user-select: none;
      pointer-events: auto;
    }}}}
    .explanation {{{{
      margin-top: 20px;
      white-space: pre-wrap;
      color: #444;
      text-align: left;
      max-width: 90vw;
      margin-left: auto;
      margin-right: auto;
    }}}}
    #timer {{{{ font-size: 1.1em; margin-top: 10px; }}}}
    @keyframes fall {{{{
      0% {{{{ transform: translateY(-50px) rotate(0deg); opacity: 0.8; }}}}
      100% {{{{ transform: translateY(100vh) rotate(360deg); opacity: 0; }}}}
    }}}}
    .sakura {{{{
      position: fixed;
      top: -50px;
      font-size: 24px;
      pointer-events: none;
      color: pink;
      animation: fall linear 12s;
      z-index: 9999;
      user-select: none;
    }}}}
  </style>
</head>
<body>
<h1>日本の生活(仮)</h1>
<div id="start-buttons"></div>
<div id="container"></div>
<div id="timer">時間: 0秒</div>

<script>
const allQuestions = {questions_json};
const audioData = {audio_json};

let currentCategory = null;
let questions = [];
let currentIndex = 0;
let score = 0;
let startTime = null;
let timerInterval = null;

function createButton(text, onClick) {{
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = 'category-btn';
    btn.onclick = onClick;
    return btn;
}}

function showCategories() {{
    const container = document.getElementById('start-buttons');
    container.style.display = 'block';
    container.innerHTML = '';
    for (const category in allQuestions) {{
        const btn = createButton(category, () => {{
            startQuiz(category);
        }});
        container.appendChild(btn);
    }}
    document.getElementById('container').innerHTML = '';
    document.getElementById('timer').textContent = '時間: 0秒';
}}

function startTimer() {{
    startTime = Date.now();
    timerInterval = setInterval(() => {{
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        document.getElementById('timer').textContent = '時間: ' + elapsed + '秒';
    }}, 1000);
}}

function stopTimer() {{
    clearInterval(timerInterval);
}}

function startQuiz(category) {{
    currentCategory = category;
    questions = allQuestions[category];
    currentIndex = 0;
    score = 0;
    document.getElementById('start-buttons').style.display = 'none';
    showQuestion();
    startTimer();
}}

function showQuestion() {{
    const q = questions[currentIndex];
    const container = document.getElementById('container');
    container.innerHTML = '';

    const qElem = document.createElement('div');
    qElem.textContent = q.question;
    qElem.style.whiteSpace = 'pre-wrap';
    qElem.style.fontWeight = 'bold';
    qElem.style.fontSize = '1.2em';
    container.appendChild(qElem);

    q.choices.forEach(choice => {{
        const choiceDiv = document.createElement('div');
        choiceDiv.className = 'choice';
        choiceDiv.textContent = choice;
        choiceDiv.style.textAlign = 'left';

        if (q.correct.includes(choice)) {{
            let audioFileName = `${{q.category}}-${{q.number}}-正答1.mp3`.replace(/\\n/g,'').replace(/ /g,'');
            let audioSrc = audioData[audioFileName];
            if (audioSrc) {{
                const speaker = document.createElement('span');
                speaker.className = 'speaker-icon';
                speaker.innerHTML = '🔊';
                speaker.onclick = (e) => {{
                    e.stopPropagation();
                    const audio = new Audio(audioSrc);
                    audio.play();
                }};
                choiceDiv.appendChild(speaker);
            }}
        }}

        choiceDiv.onclick = () => {{
            if (container.classList.contains('disabled')) return;
            container.classList.add('disabled');
            if (q.correct.includes(choice)) {{
                score++;
                markChoice(choiceDiv, true);
            }} else {{
                markChoice(choiceDiv, false);
            }}
            showExplanation();
        }};
        container.appendChild(choiceDiv);
    }});
}}

function markChoice(choiceDiv, isCorrect) {{
    const mark = document.createElement('span');
    mark.className = 'mark';
    mark.textContent = isCorrect ? '〇' : '×';
    choiceDiv.appendChild(mark);
}}

function showExplanation() {{
    const container = document.getElementById('container');
    const q = questions[currentIndex];

    const explanationDiv = document.createElement('div');
    explanationDiv.className = 'explanation';
    explanationDiv.textContent = q.explanation || '解説はありません。';
    container.appendChild(explanationDiv);

    const nextBtn = createButton('次へ', () => {{
        currentIndex++;
        if (currentIndex < questions.length) {{
            showQuestion();
        }} else {{
            showResult();
        }}
    }});
    container.appendChild(nextBtn);
}}

function showResult() {{
    stopTimer();
    const container = document.getElementById('container');
    container.innerHTML = '';

    const percent = Math.round((score / questions.length) * 100);
    const resultText = document.createElement('div');
    resultText.style.fontWeight = 'bold';
    resultText.style.fontSize = '1.3em';
    resultText.textContent = `正答率: ${{percent}}% (${score} / ${questions.length})`;
    container.appendChild(resultText);

    if (percent >= 90) {{
        for(let i=0; i<30; i++) {{
            const sakura = document.createElement('div');
            sakura.className = 'sakura';
            sakura.textContent = '🌸';
            sakura.style.left = Math.random() * 100 + 'vw';
            sakura.style.animationDuration = (6 + Math.random() * 6) + 's';
            sakura.style.fontSize = (16 + Math.random() * 24) + 'px';
            document.body.appendChild(sakura);
            setTimeout(() => {{
                sakura.remove();
            }}, 12000);
        }}
    }}

    const restartBtn = createButton('カテゴリ選択に戻る', () => {{
        document.getElementById('start-buttons').style.display = 'block';
        showCategories();
    }});
    container.appendChild(restartBtn);
}}

showCategories();
</script>
</body>
</html>
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ 完成: {output_file}")
