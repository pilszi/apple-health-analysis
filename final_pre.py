import pandas as pd

# file = "workout_final"
file_path = f'./static/data/apple_health_export'

df_workout = pd.read_csv(f'{file_path}/workout_final.csv')
df_hr = pd.read_csv(f'{file_path}/hr_final.csv')

# print(df_workout.head())
# print(df_hr.head())

df_workout['startDate'] = pd.to_datetime(df_workout['startDate'])
df_workout['endDate'] = pd.to_datetime(df_workout['endDate'])
df_hr['timestamp'] = pd.to_datetime(df_hr['timestamp'])
# 심박수 데이터 시간순 정렬
df_hr = df_hr.sort_values('timestamp')

workout_hr_summary = []

for idx, workout in df_workout.iterrows():
    w_start = workout['startDate']
    w_end = workout['endDate']
    
    # [핵심 로직] 해당 운동 시간 안에 포함되는 심박수만 필터링 (구간 쿼리)
    matched_hr = df_hr[(df_hr['timestamp'] >= w_start) & (df_hr['timestamp'] <= w_end)]
    # print(matched_hr)

    if not matched_hr.empty:
        # 해당 운동을 하는 동안의 심박수 통계 계산
        workout_hr_summary.append({
            'workout_idx': idx, # 매핑용 고유 키
            'workout_avg_hr': f"{matched_hr['heart_rate'].mean():.2f}", # 운동 중 평균 심박수
            'workout_max_hr': f"{matched_hr['heart_rate'].max():.2f}",  # 운동 중 최고 심박수
            'workout_min_hr': f"{matched_hr['heart_rate'].min():.2f}",  # 운동 중 최저 심박수
        })
    else:
        # 간혹 심박수 측정이 누락된 운동 세션이 있을 경우
        workout_hr_summary.append({
            'workout_idx': idx,
            'workout_avg_hr': None,
            'workout_max_hr': None,
            'workout_min_hr': None
        })

# print(workout_hr_summary)
df_workout_hr_mapped = pd.DataFrame(workout_hr_summary)
# print(df_wh.head())

# 6. 원본 운동 세션 테이블과 고유 인덱스 기준으로 결합 (Merge)
df_workout_final_mart = pd.merge(
    df_workout.reset_index().rename(columns={'index': 'workout_idx'}),
    df_workout_hr_mapped,
    on='workout_idx',
    how='left'
).drop(columns=['workout_idx']) # 임시 키 제거

df_workout_final_mart["workoutActivityType"] = df_workout_final_mart[
        "workoutActivityType"
    ].str.replace("HKWorkoutActivityType", "", regex=False)

df_workout_final_mart.to_csv(f"{file_path}/workout_hr.csv", index=False, encoding="utf-8-sig")
print('==== 최종 데이터 완성 ====')




# print(set_worktype)

# """
# 'HKWorkoutActivityTypeBowling', 'HKWorkoutActivityTypeCooldown', 'HKWorkoutActivityTypeBasketball', 'HKWorkoutActivityTypeStairs',
# 'HKWorkoutActivityTypeCycling', 'HKWorkoutActivityTypeCoreTraining', 'HKWorkoutActivityTypeRunning', 'HKWorkoutActivityTypeTraditionalStrengthTraining',
# 'HKWorkoutActivityTypeWalking'

# """
