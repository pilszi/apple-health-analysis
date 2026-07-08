import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def correlation_df():
    file_path = f'./static/data/apple_health_export'
    result = 0
    try:
        df = pd.read_csv(f'{file_path}/workout_hr.csv')
      
        # 1. 'workoutActivityType'만 원-핫 인코딩 진행
        df_ml_final = pd.get_dummies(df, columns=["workoutActivityType"], prefix="", prefix_sep="", dtype=int)

        # 2. 상관관계도 생성
        corr = df_ml_final.corr(numeric_only=True)
        # print(df_ml_ready.info())
        # 최종 확인
        # print(df_ml_ready.dtypes)
        # 한글, - 깨짐 방지
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False 

        # 3. 상관관계 히트맵 생성
        plt.figure(figsize=(15,10))
        sns.heatmap(
            corr,
            annot=True,
            cmap='coolwarm'
        )

        plt.title('데이터간의 상관관계 히트맵', fontsize=14, pad=15)

        # 4. 상관관계도 및 히트맵 저장
        plt.savefig(f"./static/img/work_hr_corr.png", dpi=300, bbox_inches="tight")
        # plt.show()
        print(" ==== Correlation 히트맵 완성 ==== ")
        plt.close()

        # 5. 총 소모 칼로리와 관계가 깊은 데이터 확인
        target_corr = corr.loc['TotalEnergyBurned']
            
        # 불필요한 더미 변수 및 자기 자신 제외
        exclude_cols = ['TotalEnergyBurned', 'Bowling', 'CoreTraining', 'Cycling', 'Running', 'TraditionalStrengthTraining', 'Walking']
        target_corr = target_corr.drop(labels=exclude_cols, errors='ignore')
        
        # 절대값 기준 내림차순 정렬
        target_corr_sorted = target_corr.reindex(target_corr.abs().sort_values(ascending=False).index)
        # 한글, - 깨짐 방지
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False 

        # 가로 막대 그래프 그리기
        plt.figure(figsize=(10, 6))
        colors = sns.color_palette("coolwarm", len(target_corr_sorted))
        sns.barplot(x=target_corr_sorted.values, y=target_corr_sorted.index, palette=colors)
        
        # 그래프 세부 레이아웃 설정
        plt.axvline(x=0, color='gray', linestyle='--', linewidth=1)
        plt.title('TotalEnergyBurned(총 칼로리 소모량)와의 주요 지표별 상관관계', fontsize=14, pad=15)
        plt.xlabel('상관계수 (Correlation Coefficient)', fontsize=11)
        plt.ylabel('측정 지표', fontsize=11)
        plt.xlim(-1, 1)
        
        # 막대 끝에 숫자 표시
        for i, val in enumerate(target_corr_sorted.values):
            plt.text(val + (0.02 if val >= 0 else -0.07), i, f"{val:.3f}", va='center', fontsize=10, fontweight='bold')
        
        # 칼로리 중심 그래프 저장
        plt.savefig(f"./static/img/total_energy_burned_corr.png", dpi=300, bbox_inches="tight")
        plt.close()
        print(" ==== 칼로리 중심 상관관계 그래프 완성 ==== ")

        # 6. 상관관계도 CSV 저장
        corr.to_csv(f"{file_path}/work_hr_corr.csv")
        print(" ==== Correlation 완성 ==== ")
        result = 1


        result = 1
    except FileNotFoundError as f:
        print(f"파일을 찾지 못했습니다 : {f}")
    except Exception as e:
        print(f"기타 에러 발생 : {e}")
    return result
