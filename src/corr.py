import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def correlation_df():
    file_path = f'./static/data/apple_health_export'
    try:
        df = pd.read_csv(f'{file_path}/workout_hr.csv')
      
        # 1. 'workoutActivityType'만 원-핫 인코딩 진행
        df_ml_final = pd.get_dummies(df, columns=["workoutActivityType"], prefix="", prefix_sep="", dtype=int)

        # 2. 상관관계도 생성
        corr = df_ml_final.corr(numeric_only=True)
        # print(df_ml_ready.info())
        # 최종 확인
        # print(df_ml_ready.dtypes)
        
        # 3. 상관관계 히트맵 생성
        plt.figure(figsize=(12,8))
        sns.heatmap(
            corr,
            annot=True,
            cmap='coolwarm'
        )
        # 4. 상관관계도 및 히트맵 저장
        corr.to_csv(f"{file_path}/work_hr_corr.csv")
        plt.savefig(f"./static/img/work_hr_corr.png", dpi=300, bbox_inches="tight")
        print(" ==== Correlation 완성 ==== ")
    except FileNotFoundError as f:
        print(f"파일을 찾지 못했습니다 : {f}")
    except Exception as e:
        print(f"기타 에러 발생 : {e}")
