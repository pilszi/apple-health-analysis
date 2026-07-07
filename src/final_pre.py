import pandas as pd

def pre_ml_data():
    """
        머신러닝 학습을 위한 데이터 컬럼 정리
    """
    file_path = f'./static/data/apple_health_export'
    result = 0
    try:
        df_workout = pd.read_csv(f'{file_path}/workout_pre.csv')
        df_hr = pd.read_csv(f'{file_path}/hr_pre.csv')

        # print(df_workout.head())
        # print(df_hr.head())
        df_workout['startDate'] = pd.to_datetime(df_workout['startDate'])
        df_workout['endDate'] = pd.to_datetime(df_workout['endDate'])
        df_hr['startDate'] = pd.to_datetime(df_hr['startDate'])
        # 심박수 데이터 시간순 정렬
        df_hr = df_hr.sort_values('startDate')

        # 1. 운동 중 심박수 평균, 최고, 최저 수치 
        workout_hr_summary = []
        for idx, workout in df_workout.iterrows():
            w_start = workout['startDate']
            w_end = workout['endDate']
            
            # 해당 운동 시간 안에 포함되는 심박수만 필터링
            matched_hr = df_hr[(df_hr['startDate'] >= w_start) & (df_hr['startDate'] <= w_end)]
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

        df_workout_hr_mapped = pd.DataFrame(workout_hr_summary)

        df_hr["startDate"] = pd.to_datetime(df_workout["startDate"])

        # 2. 파생 변수 생성 (운동 시작 시간, 주말/평일 구분)
        df_workout_hr_mapped["start_hour"] = df_hr["startDate"].dt.hour  # 0 ~ 23시 (수치형)
        df_workout_hr_mapped["is_weekend"] = (
            df_hr["startDate"].dt.weekday >= 5
        ).astype(  # 5, 6이 토, 일요일
            int
        )  # 주말이면 1, 평일이면 0 (이진형)

        # 3. 갯수가 부족한 데이터 제거
        value = df_workout["workoutActivityType"].value_counts()
        valid_types = value[value >= 20].index
        df_workout_ = df_workout[df_workout["workoutActivityType"].isin(valid_types)]
        # print(workout_hr_summary)

        # 4. doration < 20 인 데이터 제거(운동시간 20분 이상인 데이터만 취급)
        min_value = df_workout_["duration"] >= 20
        df_workout_ = df_workout_[min_value]
        

        # 5. 원본 운동 세션 테이블과 고유 인덱스 기준으로 결합 (Merge)
        df_workout_hr_merge = pd.merge(
            df_workout_.reset_index().rename(columns={'index': 'workout_idx'}),
            df_workout_hr_mapped,
            on='workout_idx',
            how='left'
        ).drop(columns=['workout_idx']) # 임시 키 제거

        # 6. 독립변수 추가
        df_workout_hr_merge["TotalEnergyBurned"] = (df_workout_hr_merge["ActiveEnergyBurned"].astype(float) + df_workout_hr_merge["BasalEnergyBurned"].astype(float))     # 활동 소모 칼로리 + 기초 대사 소모 칼로리
        df_workout_hr_merge['hr_variability'] = (df_workout_hr_merge['workout_max_hr'].astype(float) - df_workout_hr_merge['workout_min_hr'].astype(float))               # 안정성 및 인터벌 강도
        df_workout_hr_merge['hr_sustain_ratio'] = (df_workout_hr_merge['workout_avg_hr'].astype(float) / df_workout_hr_merge['workout_max_hr'].astype(float))             # 운동 지속성 및 유지력
        df_workout_hr_merge["training_load"] = (df_workout_hr_merge["duration"].astype(float) * df_workout_hr_merge["workout_avg_hr"].astype(float))                      # 운동 총량 지표
        df_workout_hr_merge["calories_per_min"] = (df_workout_hr_merge["TotalEnergyBurned"].astype(float) / df_workout_hr_merge["duration"].astype(float))                # 분당 소모 칼로리

        # 7. 분석 및 원-핫 인코딩 단계에서 제외할 컬럼 정의
        drop_cols = ["startDate", "endDate", "ActiveEnergyBurned", "BasalEnergyBurned"]
        df_workout_hr_merge = df_workout_hr_merge.drop(columns=drop_cols, errors="ignore")

        df_workout_hr_merge.to_csv(f"{file_path}/workout_hr.csv", index=False, encoding="utf-8-sig")
        print('==== 최종 데이터 완성 ====')
        result = 1
    except FileNotFoundError as f:
        print(f"파일을 찾지 못했습니다 : {f}")
    except KeyError as k:
        print(f"key 에러 발생 : {k}")
    except Exception as e:
        print(f"기타 에러 발생 : {e}")
    return result

