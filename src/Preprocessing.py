import pandas as pd

def PreProcess(file):
    """
        csv 파일 전처리 함수

        file_path : csv file이 저장된 경로
    """
    file_path = f'./static/data/apple_health_export/{file}.csv'
    df = pd.read_csv(file_path)

    print(f'{df.head()}')

    # 결측치 확인
    print(df.info())
    if df.isna().sum().sum() > 0:
        df.dropna()
    print("="*60)

    # 중복값 확인
    print(df.duplicated().sum())
    if df.duplicated().sum() > 0:
        df.drop_duplicates(inplace=True)
    print("="*60)

    # 모든 데이터 날짜 맞추기
    print(f"2026-5-15 이전 데이터 수 = {len(df[df['date'] < '2021-05-15'])}")
    df = df[df["date"] >= "2021-05-15"]
    print(df.head())
    df.to_csv(f'./static/data/apple_health_export/{file}_final.csv', index=False, encoding="utf-8-sig")
    print(f"==== {file}_final.csv 생성 ====")
    


preprocessing("workout")

# """
#     workout 테이블에서 운동 타입 종류
#     'HKWorkoutActivityTypeRunning', 'HKWorkoutActivityTypeWalking', 'HKWorkoutActivityTypeCycling', 'HKWorkoutActivityTypeTraditionalStrengthTraining',
#     'HKWorkoutActivityTypeBasketball', 'HKWorkoutActivityTypeStairs', 'HKWorkoutActivityTypeBowling', 'HKWorkoutActivityTypeCoreTraining', 'HKWorkoutActivityTypeCooldown'
# """

