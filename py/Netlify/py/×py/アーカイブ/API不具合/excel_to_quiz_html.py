import pandas as pd
import json
import random

input_file = "quiz_questions.xlsx"
output_file = "日本の生活.html"

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

    q_obj = {
        "question": question_text,
        "correct": correct,
        "choices": choices,
        "explanation": explanation
    }

    questions_by_category.setdefault(category, []).append(q_obj)

for key in questions_by_category:
    random.shuffle(questions_by_category[key])

html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>日本の生活(仮)</title>
<style>
  body {{ font-family: sans-serif; background: #FFEFD5; text-align: center; padding: 10px 5px; }}
  .category-btn, #next, #restart {{
    padding: 14px 28px; font-size: 1.3em; margin: 10px auto; max-width: 300px; background-color: orange;
    color: white; border: none; border-radius: 12px; cursor: pointer; white-space: pre-line; display: block;
  }}
  .choice {{
    display: block; margin: 8px auto; padding: 14px 16px; font-size: 1.2em; max-width: 90vw;
    background-color: #ADD8E6; border-radius: 12px; position: relative; cursor: pointer;
    white-space: pre-wrap; text-align: left; word-break: break-word;
  }}
  .chosen {{ background-color: #87b4cc; }}
  .disabled {{ pointer-events: none; }}
  .mark {{
    position: absolute; top: 50%; left: 20px; transform: translateY(-50%);
    font-size: 2em; font-weight: bold; color: red;
  }}
.speaker-icon {{
  cursor: pointer;
  font-size: 1.5em;
  color: #444;
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}}

  .explanation {{
    margin-top: 20px; white-space: pre-wrap; color: #444; text-align: left;
    max-width: 90vw; margin-left: auto; margin-right: auto;
  }}
  #timer {{ font-size: 1.1em; margin-top: 10px; }}
  @keyframes fall {{
    0% {{ transform: translateY(-50px) rotate(0deg); opacity: 0.8; }}
    100% {{ transform: translateY(100vh) rotate(360deg); opacity: 0; }}
  }}
  .sakura {{
    position: fixed; top: -50px; font-size: 24px; pointer-events: none;
    color: pink; animation: fall linear 12s; z-index: 9999;
  }}
</style>
</head>
<body>
<h1>日本の生活(仮)</h1>
<div id="container"></div>
<div id="timer">時間: 0秒</div>
<script>
const allQuestions = {json.dumps(questions_by_category, ensure_ascii=False, indent=2)};

let currentQuestions = [];
let currentQuestionIndex = 0;
let score = 0;
let selectedAnswers = [];
let startTime, timerInterval;
const container = document.getElementById("container");
const timer = document.getElementById("timer");
let sakuraInterval;

function createSakura() {{
  const sakura = document.createElement("div");
  sakura.className = "sakura";
  sakura.textContent = "🌸";
  sakura.style.left = Math.random() * 100 + "vw";
  sakura.style.animationDuration = (10 + Math.random() * 5) + "s";
  sakura.style.fontSize = (16 + Math.random() * 20) + "px";
  document.body.appendChild(sakura);
  setTimeout(() => sakura.remove(), 15000);
}}

function startSakuraFall() {{
  createSakura();
  sakuraInterval = setInterval(createSakura, 400);
}}

function stopSakuraFall() {{
  clearInterval(sakuraInterval);
  document.querySelectorAll(".sakura").forEach(el => el.remove());
}}

function startCategory(name) {{
  currentQuestions = allQuestions[name];
  currentQuestionIndex = 0;
  score = 0;
  startTime = Date.now();
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {{
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    timer.textContent = `時間: ${{elapsed}}秒`;
  }}, 1000);
  showQuestion();
}}

function showCategoryButtons() {{
  stopSakuraFall();
  container.innerHTML = "";
  for (let key in allQuestions) {{
    const btn = document.createElement("button");
    btn.className = "category-btn";
    btn.textContent = key;
    btn.onclick = () => startCategory(key);
    container.appendChild(btn);
  }}
  timer.textContent = "時間: 0秒";
}}

function showQuestion() {{
  const q = currentQuestions[currentQuestionIndex];
  container.innerHTML = `<div id="question" style="white-space: pre-wrap; text-align:left; max-width:90vw; margin: 0 auto 20px auto;">${{q.question}}</div>`;
  selectedAnswers = [];
  const shuffled = [...q.choices].sort(() => Math.random() - 0.5);
  shuffled.forEach(choice => {{
    const btn = document.createElement("div");
    btn.className = "choice";
    btn.textContent = choice;
    btn.onclick = () => handleChoice(btn, choice, q);
    container.appendChild(btn);
  }});
}}

function handleChoice(btn, choice, q) {{
  if (selectedAnswers.includes(choice)) {{
    selectedAnswers = selectedAnswers.filter(c => c !== choice);
    btn.classList.remove("chosen");
    return;
  }}
  if (selectedAnswers.length >= q.correct.length) return;
  selectedAnswers.push(choice);
  btn.classList.add("chosen");

  if (selectedAnswers.length === q.correct.length) {{
    document.querySelectorAll(".choice").forEach(b => b.classList.add("disabled"));
    selectedAnswers.forEach(sel => {{
      const target = [...document.querySelectorAll(".choice")].find(b => b.textContent === sel);
      const mark = document.createElement("div");
      mark.className = "mark";
      mark.textContent = q.correct.includes(sel) ? "○" : "×";
      target.appendChild(mark);

if (q.correct.includes(sel)) {{
  const speaker = document.createElement("span");
  speaker.className = "speaker-icon";
  speaker.textContent = "🔊";
  speaker.style.cursor = "pointer";
  speaker.onclick = function() {{
    const jaOnly = sel.split(/\\n|（|。|\\(|\\u3000|\\s/)[0];
    const utter = new SpeechSynthesisUtterance(jaOnly);
    utter.lang = "ja-JP";
    speechSynthesis.cancel();  // 直前の音声を止める
    speechSynthesis.speak(utter);
  }};
  target.appendChild(speaker);
}}



    }});

    if (selectedAnswers.every(ans => q.correct.includes(ans))) score++;

    if (q.explanation) {{
      const ex = document.createElement("div");
      ex.className = "explanation";
      ex.textContent = q.explanation;
      container.appendChild(ex);
    }}

    const next = document.createElement("button");
    next.id = "next";
    next.textContent = "つぎへ";
    next.onclick = () => {{
      currentQuestionIndex++;
      if(currentQuestionIndex < currentQuestions.length) showQuestion();
      else showResult();
    }};
    container.appendChild(next);
  }}
}}

function showResult() {{
  clearInterval(timerInterval);
  const percent = Math.round((score / currentQuestions.length) * 100);
  const timeTaken = Math.floor((Date.now() - startTime) / 1000);
  const today = new Date();
  const dateStr = `${{today.getFullYear()}}/${{today.getMonth()+1}}/${{today.getDate()}}`;
  container.innerHTML = `<p>日付: ${{dateStr}}</p><p>正解数：${{score}} / ${{currentQuestions.length}}</p><p>正答率：${{percent}}%</p><p>回答時間：${{timeTaken}}秒</p>`;
  if (percent >= 90) startSakuraFall();

  const restart = document.createElement("button");
  restart.id = "restart";
  restart.textContent = "さいしょから";
  restart.onclick = () => {{
    stopSakuraFall();
    showCategoryButtons();
  }};
  container.appendChild(restart);
}}

showCategoryButtons();
</script>
</body>
</html>
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"「{output_file}」を出力しました。")
