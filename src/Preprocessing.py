import pandas as pd

def PreProcess():
    """
        csv 파일 전처리 함수
        (결측치, 중복값, 불필요한 데이터 삭제)

    """
    file_path = f'./static/data/apple_health_export'
    result = 0
    try:
        df_workout = pd.read_csv(f"{file_path}/workout.csv")
        df_hr = pd.read_csv(f"{file_path}/hr.csv")
        df_li = [(df_workout, "workout"), (df_hr, "hr")]
        for df, filename in df_li:
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
            df.to_csv(f'./static/data/apple_health_export/{filename}_pre.csv', index=False, encoding="utf-8-sig")
            print(f"==== {filename}_pre.csv 생성 ====")
            result = 1
    except FileNotFoundError as f:
        print(f"파일을 찾지 못했습니다 : {f}")
    except Exception as e:
        print(f"기타 에러 발생 : {e}")
    return result
