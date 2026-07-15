import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
import joblib
from db import con


def ml_train_test_split():
    encoder = OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False)

    # file_path = f'./static/data/apple_health_export'
    # df = pd.read_csv(f'{file_path}/workout_hr.csv')
    conn = con()
    sql = """ 
        SELECT workout_date, workoutactivitytype, duration, 
                workout_avg_hr, workout_max_hr, workout_min_hr, 
                training_load, totalenergyburned
        FROM apple_health
    """
    df = pd.read_sql(sql, conn)
    print(f"==== {len(df)}건의 데이터를 성공적으로 불러왔습니다 ====")
    df.columns = df.columns.str.lower()
    print(df.columns)
    #'workoutActivityType', 'duration', 'date', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr', 'TotalEnergyBurned', 'hr_variability', 'hr_sustain_ratio', 'training_load', 'calories_per_min'

    # 1. 독립변수 조정
    x = df[['workoutactivitytype', 'duration', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr', 'training_load']]

    # 2. 종속변수
    y = df['totalenergyburned']

    # 3. 훈련, 시험 데이터 분리
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, shuffle=True)

    # 4. 범주형 데이터 수치형으로 인코딩
    x_train_cat = encoder.fit_transform(x_train[['workoutactivitytype']])
    x_test_cat = encoder.transform(x_test[['workoutactivitytype']])

    # 5. 수치형 데이터 지정
    x_train_num = x_train.drop(columns="workoutactivitytype")
    x_test_num = x_test.drop(columns="workoutactivitytype")

    # 6. 범주형 데이터 항목 이름
    cols = encoder.get_feature_names_out(['workoutactivitytype'])

    # 7. 인코딩 한 범주형 데이터 데이터프레임 변경
    x_train_cat_df = pd.DataFrame(x_train_cat, columns= cols, index= x_train.index)
    x_test_cat_df = pd.DataFrame(x_test_cat, columns= cols, index= x_test.index)

    # 8. 범주형 데이터, 수치형 데이터를 합쳐 하나의 데이터프레임으로 생성
    x_train_final = pd.concat([x_train_cat_df, x_train_num], axis= 1)
    x_test_final =pd.concat([x_test_cat_df, x_test_num], axis= 1)

    # encoder, 머신러닝 학습 컬럼 순서 저장
    joblib.dump(encoder, './static/model/encoder.pkl')
    joblib.dump(x_train_final.columns.to_list(), './static/model/apple_health_cols.pkl')
    print(" ==== 학습 데이터 분리 완료 ==== ")
    
    return [x_train_final, x_test_final, y_train, y_test]

# print(x_train_final.shape, y_train.shape)

def ml_train(x_train, x_test, y_train, y_test):
    
    res = 0
    result = []
    try:
        for i in range(5, 15):
            model = RandomForestRegressor(random_state=42, max_depth=i)
            # 1. 모델 학습 및 테스트
            model.fit(x_train, y_train)
            pred = model.predict(x_test)
            r2s = r2_score(y_test, pred)

            # 2. 모델 학습시 가중치 확인
            importance = pd.Series(
                model.feature_importances_,
                index=x_train.columns
            ).sort_values(ascending=False)
            
            # 3. 실제 값과 예측 값의 오차 확인
            mae = mean_absolute_error(y_test, pred)

            # 4. 실제 값과 예측 값 시각화
            plt.figure(figsize=(6,6))
            plt.scatter(y_test, pred, alpha=0.5)
            plt.xlabel("Actual")
            plt.ylabel("Predicted")
            plt.plot(
                [y_test.min(), y_test.max()],
                [y_test.min(), y_test.max()],
                "r--"
            )
            plt.savefig(f"./static/img/actual_vs_predicted_{i}.png", dpi=300, bbox_inches="tight")
            # plt.show()

            # 5. depth 에 따른 모델 학습 결과 저장
            result.append({
                "model": model,
                "depth": i,
                "score": r2s,
                "mean_error": mae,
                "importance": importance
            })
        # 6. result 에서의 메타 정보를 하나의 리스트로 생성
        rows = []
        try:
            for item in result:
                row = {
                    'depth': item['depth'],
                    'score': item['score'],
                    'mean_error': item['mean_error']
                }

                # item['importance']는 pd.Series 형태이므로 딕셔너리처럼 순회하며 컬럼으로 추가
                for feature_name, value in item['importance'].items():
                    row[feature_name] = value

                rows.append(row)

            # 7. 학습 결과 csv 파일 저장 및 학습 모델 파일 저장
            df_final = pd.DataFrame(rows)            
            df_final.to_csv('./static/model/model_result.csv', index=False, encoding='utf-8-sig')
            for r in result:
                joblib.dump(r['model'], f'./static/model/RF_model_{r["depth"]}.pkl')
        except Exception as e:
            print(f"에러 발생 : {e}")
        res = 1
        print(" ==== 모델 학습 완료 ==== ")
    except Exception as e:
        print(f" ==== 에러 발생 : {e} ==== ")

    return res
    