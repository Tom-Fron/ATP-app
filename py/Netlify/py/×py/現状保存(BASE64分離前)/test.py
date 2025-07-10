import pandas as pd

df = pd.read_excel("quiz_questions.xlsx")
print("P10:", df.iloc[9, 15])  # P10の内容表示
print("Q10:", df.iloc[9, 16])  # Q10の内容表示
