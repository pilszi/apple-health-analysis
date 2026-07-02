import pandas as pd

# 날짜, 시간을 수치형 데이터로 변경 ( 주말이면 1, 평일이면 0 / 운동 시작 시간만 수치형 데이터로 추출 )
file_path = f'./static/data/apple_health_export'
df_workout_hr = pd.read_csv(f'{file_path}/workout_hr.csv')

# 1. 시계열(Datetime) 객체로 임시 변환 ( type : str -> datetime64[us, UTC+09:00] )
df_workout_hr["startDate"] = pd.to_datetime(df_workout_hr["startDate"])

# 2. 파생 변수 생성 (차원을 늘리지 않는 방식)
df_workout_hr["start_hour"] = df_workout_hr["startDate"].dt.hour  # 0 ~ 23시 (수치형)
df_workout_hr["is_weekend"] = (
    df_workout_hr["startDate"].dt.weekday >= 5
).astype(  # 5, 6이 토, 일요일
    int
)  # 주말이면 1, 평일이면 0 (이진형)

df_workout_hr["TotalEnergyBurned"] = (df_workout_hr["ActiveEnergyBurned"] + df_workout_hr["BasalEnergyBurned"])
df_workout_hr['heart_rate_range'] = (df_workout_hr['workout_max_hr'] - df_workout_hr['workout_min_hr'])
df_workout_hr['hr_avg_ratio'] = (df_workout_hr['workout_avg_hr']/df_workout_hr['workout_max_hr'])
df_workout_hr["duration/hr"] = (df_workout_hr["duration"] * df_workout_hr["workout_avg_hr"])

# 3. 분석 및 원-핫 인코딩 단계에서 제외할 컬럼 정의
drop_cols = ["startDate", "endDate", "ActiveEnergyBurned", "BasalEnergyBurned"]
df_workout_hr = df_workout_hr.drop(columns=drop_cols, errors="ignore")

# 4. 데이터 갯수가 부족한 데이터 제거
value = df_workout_hr["workoutActivityType"].value_counts()
valid_types = value[value >= 20].index
df_ml_ready = df_workout_hr[df_workout_hr["workoutActivityType"].isin(valid_types)]

# 5. 'workoutActivityType'만 원-핫 인코딩 진행
df_ml_final = pd.get_dummies(df_ml_ready, columns=["workoutActivityType"], dtype=int)

# print(df_ml_ready.info())
# 최종 확인
# print(df_ml_ready.dtypes)
df_ml_ready.to_csv(f"{file_path}/work_hr_final.csv", index=False, encoding="utf-8-sig")
df_ml_final.corr(numeric_only=True).to_csv(f"{file_path}/work_hr_corr.csv")
print(" ==== Correlation 완성 ==== ")