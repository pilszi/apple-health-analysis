import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False)

file_path = f'./static/data/apple_health_export'
df_workout_hr = pd.read_csv(f'{file_path}/work_hr_final.csv')


# print(df_workout_hr.columns)
# ['workoutActivityType', 'duration', 'date', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr', 'start_hour', 'is_weekend', 'TotalEnergyBurned', 'heart_rate_range', 'hr_avg_ratio', 'duration/hr']

# 1. 독립변수 조정
# x = df_workout_hr[['workoutActivityType', 'duration', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr']]
# x= df_workout_hr[['workoutActivityType', 'duration', 'workout_avg_hr']]
# x= df_workout_hr[['workoutActivityType', 'duration', 'workout_avg_hr', 'heart_rate_range']]
x = df_workout_hr[['workoutActivityType', 'duration', 'hr_avg_ratio','duration/hr']]

# 2. 종속변수
y = df_workout_hr['TotalEnergyBurned']

# 3. 훈련, 시험 데이터 분리
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, shuffle=True)

# 4. 범주형 데이터 수치형으로 인코딩
x_train_cat = encoder.fit_transform(x_train[['workoutActivityType']])
x_test_cat = encoder.transform(x_test[['workoutActivityType']])

# 5. 수치형 데이터 지정
# x_train_num = x_train[['duration', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr']]
# x_test_num = x_test[['duration', 'workout_avg_hr', 'workout_max_hr', 'workout_min_hr']]
# x_train_num = x_train[['duration', 'workout_avg_hr', 'heart_rate_range']]
# x_test_num = x_test[['duration', 'workout_avg_hr', 'heart_rate_range']]
# x_train_num = x_train[['duration', 'workout_avg_hr']]
# x_test_num = x_test[['duration', 'workout_avg_hr']]
x_train_num = x_train[['duration', 'hr_avg_ratio','duration/hr']]
x_test_num = x_test[['duration', 'hr_avg_ratio','duration/hr']]

# 6. 범주형 데이터 항목 이름
cols = encoder.get_feature_names_out(['workoutActivityType'])

# 7. 인코딩 한 범주형 데이터 데이터프레임 변경
x_train_cat_df = pd.DataFrame(x_train_cat, columns= cols, index= x_train.index)
x_test_cat_df = pd.DataFrame(x_test_cat, columns= cols, index= x_test.index)

# 8. 범주형 데이터, 수치형 데이터를 합쳐 하나의 데이터프레임으로 생성
x_train_final = pd.concat([x_train_cat_df, x_train_num], axis= 1)
x_test_final =pd.concat([x_test_cat_df, x_test_num], axis= 1)

print(x_train_final.shape, y_train.shape)