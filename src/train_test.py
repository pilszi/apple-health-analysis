import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
import joblib

encoder = OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False)

file_path = f'./static/data/apple_health_export'
df = pd.read_csv(f'{file_path}/workout_hr.csv')

# print(df_workout_hr.columns)
#'workoutActivityType', 'duration', 'date', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr', 'TotalEnergyBurned', 'hr_variability', 'hr_sustain_ratio', 'training_load', 'calories_per_min'

# 1. 독립변수 조정
x = df[['workoutActivityType', 'duration', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr', 'training_load']]

# 2. 종속변수
y = df['TotalEnergyBurned']

# 3. 훈련, 시험 데이터 분리
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, shuffle=True)

# 4. 범주형 데이터 수치형으로 인코딩
x_train_cat = encoder.fit_transform(x_train[['workoutActivityType']])
x_test_cat = encoder.transform(x_test[['workoutActivityType']])

# 5. 수치형 데이터 지정
x_train_num = x_train.drop(columns="workoutActivityType")
x_test_num = x_test.drop(columns="workoutActivityType")

# 6. 범주형 데이터 항목 이름
cols = encoder.get_feature_names_out(['workoutActivityType'])

# 7. 인코딩 한 범주형 데이터 데이터프레임 변경
x_train_cat_df = pd.DataFrame(x_train_cat, columns= cols, index= x_train.index)
x_test_cat_df = pd.DataFrame(x_test_cat, columns= cols, index= x_test.index)

# 8. 범주형 데이터, 수치형 데이터를 합쳐 하나의 데이터프레임으로 생성
x_train_final = pd.concat([x_train_cat_df, x_train_num], axis= 1)
x_test_final =pd.concat([x_test_cat_df, x_test_num], axis= 1)

# print(x_train_final.shape, y_train.shape)

result = []
for i in [5, 7]:
    model = RandomForestRegressor(random_state=42, max_depth=i)
    model.fit(x_train_final, y_train)
    pred = model.predict(x_test_final)
    r2s = r2_score(y_test, pred)

    importance = pd.Series(
        model.feature_importances_,
        index=x_train_final.columns
    ).sort_values(ascending=False)

    mae = mean_absolute_error(y_test, pred)

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
    plt.show()

    result.append({
        "model": model,
        "depth": i,
        "score": r2s,
        "mean_error": mae,
        "importance": importance
    })

rows = []
for item in result:
    # 기본 메타 정보 저장
    row = {
        'depth': item['depth'],
        'score': item['score'],
        'mean_error': item['mean_error']
    }

    # item['importance']는 pd.Series 형태이므로 딕셔너리처럼 순회하며 컬럼으로 추가
    for feature_name, value in item['importance'].items():
        row[f'importance_{feature_name}'] = value

    rows.append(row)

# 2. 데이터프레임 변환
df_final = pd.DataFrame(rows)

# 3. CSV 파일로 저장
df_final.to_csv('./static/model/model_result.csv', index=False, encoding='utf-8-sig')

for r in result:
    joblib.dump(r['model'], f'./static/model/RF_model_{r["depth"]}.pkl')
joblib.dump(encoder, './static/model/encoder.pkl')
joblib.dump(x_train_final.columns.to_list(), './static/model/apple_health_cols.pkl')