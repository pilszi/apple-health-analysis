import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def PreProcess():
    """
        csv 파일 전처리 함수
        (결측치, 중복값, 불필요한 데이터 삭제)

    """
    try:
        file_path = f'./static/data/apple_health_export'
        model = LinearRegression()
        result = 0
        df_workout = pd.read_csv(f"{file_path}/workout.csv")
        df_hr = pd.read_csv(f"{file_path}/hr.csv")
        
        # 1. 이상치 처리
        try:
            # workout 이상치 처리
            
            # 1. 운동시간 20분 미만인 데이터 제거
            min_value = df_workout["duration"] >= 20
            df_workout = df_workout[min_value]
            
            # 2. 갯수가 부족한 운동타입 제거
            value = df_workout["workoutActivityType"].value_counts()
            valid_types = value[value >= 20].index
            df_workout = df_workout[df_workout["workoutActivityType"].isin(valid_types)]

            # 3. 기초 대사 칼로리 이상치 제거
            df_workout = df_workout[df_workout["BasalEnergyBurned"] < 2000]

            # 4. 활동 칼로리 이상치 확인
            model.fit(df_workout['duration'].values.reshape(-1, 1), df_workout['ActiveEnergyBurned'])
            result = model.predict(df_workout['duration'].values.reshape(-1,1))
            # 실제 값과 예측값의 오차의 절대값을 저장
            df_workout['y_pred'] = result
            df_workout['error'] = np.abs(df_workout['ActiveEnergyBurned'] - df_workout['y_pred'])
            top_errors = df_workout.sort_values(by='error', ascending=False).head(4)
            print(top_errors[['workoutActivityType', 'date', 'duration', 'ActiveEnergyBurned', 'error']])

            # 4-1. 그래프로 시각화하여 확인하기
            plt.figure(figsize=(10, 6))
            plt.scatter(df_workout['duration'], df_workout['ActiveEnergyBurned'], c= 'b')
            plt.plot(df_workout['duration'], result, c='r')
            # 가장 멀리 떨어진 점들만 빨간색 테두리로 강조 표시
            plt.scatter(top_errors['duration'], top_errors['ActiveEnergyBurned'], 
                        color='none', edgecolor='red', s=150)
            # 4-2. 강조된 점들에 오차 적어주기
            for idx, row in top_errors.iterrows():
                plt.vlines(x=row['duration'], ymin=row['ActiveEnergyBurned'], ymax=row['y_pred'], colors='gray', linestyles='dashed', alpha=0.4)
                plt.text(row['duration']- 5, row['ActiveEnergyBurned']- 80, f"error: {row['error']:.1f}")
            plt.xlabel("duration")
            plt.ylabel("ActiveEnergyBurned")
            plt.savefig(f"./static/img/workout.png", dpi=300, bbox_inches="tight")

            # 4-3. 활동 칼로리 이상치 제거
            df_workout = df_workout.drop([2400, 1958])
        except KeyError as k:
            print(f"key 가 틀렸습니다. : {k}")
        except SyntaxError as s:
            print(f"문법 오류 : {s}")
        except Exception as e:
            print(f"기타 에러 발생 : {e}")
        
        # 2. 결측치 처리
        try:    
            # workout 결측치 처리 - 온도, 습도 결측치는 선형보간으로 채우고, 그 외 컬럼 결측치는 행 제거
            nan_sum = df_workout.isna().sum()
            print(nan_sum)
            weather_cols = ['Temperature', 'Humidity']
            other_cols = [col for col in df_workout.columns if col not in weather_cols]
            df_workout = df_workout.sort_values("startDate")
            df_workout[weather_cols] = df_workout[weather_cols].interpolate(method="linear", limit_direction="both")
            df_workout.dropna(subset=other_cols, inplace=True)

            # workout 중복값 처리 - 처음 값만 남기고 모두 제거
            print(df_workout.duplicated().sum())
            if df_workout.duplicated().sum() > 0:
                df_workout.drop_duplicates(inplace=True, keep='first')
            print("="*60)
            print(f"==== workout_pre.csv 생성/ 행 : {len(df_workout)} ====")
            
        except KeyError as k:
            print(f"key 가 틀렸습니다. : {k}")
        except SyntaxError as s:
            print(f"문법 오류 : {s}")
        except Exception as e:
            print(f"기타 에러 발생 : {e}")

        # 심박수 데이터 전처리 - 전체 심박수 중 운동 중 심박수만 남기고 모두 제거
        try:
            df_hr['startDate'] = pd.to_datetime(df_hr['startDate'], format='mixed', errors='coerce')
            df_workout['startDate'] = pd.to_datetime(df_workout['startDate'], format='mixed', errors='coerce')
            df_workout['endDate'] = pd.to_datetime(df_workout['endDate'], format='mixed', errors='coerce')

            hr_li = []
            for idx, workout in df_workout.iterrows():
                start = workout['startDate']
                end = workout['endDate']
                match_hr = df_hr[df_hr['startDate'].between(start, end)]
                hr_li.append(match_hr)
            df_hr_workout = pd.concat(hr_li).drop_duplicates().sort_values('startDate')
            print(f"==== hr_pre.csv 생성/ 행 : {len(df_hr_workout)} ====")
        except KeyError as k:
            print(f"key 가 틀렸습니다. : {k}")
        except SyntaxError as s:
            print(f"문법 오류 : {s}")
        except Exception as e:
            print(f"기타 에러 발생 : {e}")
        result = 1

    except FileNotFoundError as f:
        print(f"파일을 찾지 못했습니다 : {f}")
    except KeyError as k:
            print(f"key 가 틀렸습니다. : {k}")
    except SyntaxError as s:
        print(f"문법 오류 : {s}")
    except Exception as e:
            print(f"기타 에러 발생 : {e}")
        
    return result
