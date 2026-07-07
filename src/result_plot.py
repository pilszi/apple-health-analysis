import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("./static/model/model_result.csv")

# print(df.columns)
# 'depth', 'score', 'mean_error', 'training_load', 'workout_avg_hr', 'workout_max_hr', 'workoutActivityType_Running', 'workout_min_hr', 'duration'
# 'workoutActivityType_TraditionalStrengthTraining', 'workoutActivityType_Walking', 'workoutActivityType_Cycling', 'workoutActivityType_CoreTraining'


# 1. 데이터 불러오기 및 depth 정렬
df = df.sort_values(by='depth')

# 2. 그래프 생성 (이중 Y축 설정)
fig, ax1 = plt.subplots(figsize=(10, 6))

# --- 왼쪽 Y축: score (파란색) ---
color_score = '#1f77b4'
ax1.set_xlabel('Depth', fontsize=12, labelpad=10)
ax1.set_ylabel('Score', color=color_score, fontsize=12)
line1 = ax1.plot(df['depth'], df['score']*100, marker='o', color=color_score, linewidth=2, label='Score')
ax1.tick_params(axis='y', labelcolor=color_score)
ax1.set_xticks(df['depth'])  # depth 지점 명시

# --- 오른쪽 Y축: mean_error (빨간색 계열) ---
ax2 = ax1.twinx()  # X축을 공유하는 두 번째 Y축 생성
color_error = '#d62728'
ax2.set_ylabel('Mean Error', color=color_error, fontsize=12)
line2 = ax2.plot(df['depth'], df['mean_error'], marker='s', color=color_error, linewidth=2, linestyle='--', label='Mean Error')
ax2.tick_params(axis='y', labelcolor=color_error)

# 3. 스타일링 및 범례 합치기
plt.title('Score vs Mean Error by Depth', fontsize=14, pad=15, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.5)

# 두 Y축의 범례를 하나로 묶어서 표시
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=11)

plt.tight_layout()
plt.show()