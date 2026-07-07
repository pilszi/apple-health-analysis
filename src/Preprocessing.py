import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def PreProcess():
    """
        csv 파일 전처리 함수
        (결측치, 중복값, 불필요한 데이터 삭제)

    """
    file_path = f'./static/data/apple_health_export'
    model = LinearRegression()
    result = 0
    
    # 1. 이상치 처리
    try:
        df_workout = pd.read_csv(f"{file_path}/workout.csv")
        df_hr = pd.read_csv(f"{file_path}/hr.csv")

        # 기초 대사 칼로리 이상치 제거
        df_workout = df_workout[df_workout["BasalEnergyBurned"] < 2000]

        model.fit(df_workout['duration'].values.reshape(-1, 1), df_workout['ActiveEnergyBurned'])
        result = model.predict(df_workout['duration'].values.reshape(-1,1))
        # 실제 값과 예측값의 오차의 절대값을 저장
        df_workout['y_pred'] = result
        df_workout['error'] = np.abs(df_workout['ActiveEnergyBurned'] - df_workout['y_pred'])
        top_errors = df_workout.sort_values(by='error', ascending=False).head(4)
        print(top_errors[['workoutActivityType', 'date', 'duration', 'ActiveEnergyBurned', 'error']])

        # 그래프로 시각화하여 확인하기
        plt.figure(figsize=(10, 6))
        plt.scatter(df_workout['duration'], df_workout['ActiveEnergyBurned'], c= 'b')
        plt.plot(df_workout['duration'], result, c='r')
        # 가장 멀리 떨어진 점들만 빨간색 테두리로 강조 표시
        plt.scatter(top_errors['duration'], top_errors['ActiveEnergyBurned'], 
                    color='none', edgecolor='red', s=150)
        # 강조된 점들에 오차 적어주기
        for idx, row in top_errors.iterrows():
            plt.vlines(x=row['duration'], ymin=row['ActiveEnergyBurned'], ymax=row['y_pred'], colors='gray', linestyles='dashed', alpha=0.4)
            plt.text(row['duration']- 5, row['ActiveEnergyBurned']- 80, f"error: {row['error']:.1f}")
        plt.xlabel("duration")
        plt.ylabel("ActiveEnergyBurned")
        plt.savefig(f"./static/img/workout.png", dpi=300, bbox_inches="tight")

        # 활동 칼로리 이상치 제거
        df_workout = df_workout.drop([2400, 1958])
    except FileNotFoundError as f:
        print(f"파일을 찾지 못했습니다 : {f}")
    except KeyError as k:
        print(f"key 가 틀렸습니다. : {k}")
    except Exception as e:
        print(f"기타 에러 발생 : {e}")
    
    # 2. 결측치 처리
    try:    
        df_li = [(df_workout, "workout"), (df_hr, "hr")]
        for df, filename in df_li:
            print(f'{df.head()}')

            # 결측치 확인
            print(df.info())
            if df.isna().sum().sum() > 0:
                df.dropna(inplace=True)
            print("="*60)

            # 중복값 확인
            print(df.duplicated().sum())
            if df.duplicated().sum() > 0:
                df.drop_duplicates(inplace=True)
            print("="*60)

            # 모든 데이터 날짜 맞추기
            print(f"2021-5-15 이전 데이터 수 = {len(df[df['date'] < '2021-05-15'])}")
            df = df[df["date"] >= "2021-05-15"]
            print(df.head())
            df.to_csv(f'./static/data/apple_health_export/{filename}_pre.csv', index=False, encoding="utf-8-sig")
            print(f"==== {filename}_pre.csv 생성 ====")
        result = 1
    except KeyError as k:
        print(f"key 가 틀렸습니다. : {k}")
    except SyntaxError as s:
        print(f"문법 오류 : {s}")
    except Exception as e:
        print(f"기타 에러 발생 : {e}")
    return result

PreProcess()