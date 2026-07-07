import joblib
import pandas as pd


file_path = "./static/model"

encoder = joblib.load(f"{file_path}/encoder.pkl")
cols = joblib.load(f"{file_path}/apple_health_cols.pkl")
model_5 = joblib.load(f"{file_path}/RF_model_5.pkl")
model_6 = joblib.load(f"{file_path}/RF_model_6.pkl")
model_7 = joblib.load(f"{file_path}/RF_model_7.pkl")
model_8 = joblib.load(f"{file_path}/RF_model_8.pkl")
model_9 = joblib.load(f"{file_path}/RF_model_9.pkl")
model_10 = joblib.load(f"{file_path}/RF_model_10.pkl")
model_11 = joblib.load(f"{file_path}/RF_model_11.pkl")
model_12 = joblib.load(f"{file_path}/RF_model_12.pkl")
model_13 = joblib.load(f"{file_path}/RF_model_13.pkl")
model_14 = joblib.load(f"{file_path}/RF_model_14.pkl")

# 운동타입별 max_hr, min_hr 비율
hr_ratio_type = {
    'Bowling': {'max': 1.0482, 'min': 0.9414},
    'CoreTraining': {'max': 1.0204, 'min': 0.9823},
    'Cycling': {'max': 1.0324, 'min': 0.9707},
    'Running': {'max': 1.1019, 'min': 0.8783},
    'TraditionalStrengthTraining': {'max': 1.1174, 'min': 0.8838},
    'Walking': {'max': 1.0915, 'min': 0.9212}
}

def predict_calories(model, encoder, cols, avg_hr, workout, duration):

    max_ratio = hr_ratio_type[workout]['max']
    min_ratio = hr_ratio_type[workout]['min']

    max_hr = avg_hr * max_ratio
    min_hr = avg_hr * min_ratio
    training_load = avg_hr * duration

    num_data = {
        "duration": [duration],
        "workout_avg_hr": [avg_hr],
        "workout_max_hr": [max_hr],
        "workout_min_hr": [min_hr],
        "training_load": [training_load]
    }
    cat_data = {"workoutActivityType": [workout]}

    df_num = pd.DataFrame(num_data)
    df_cat = pd.DataFrame(cat_data)

    encoder_cat = encoder.transform(df_cat)
    cat_cols = encoder.get_feature_names_out(['workoutActivityType'])
    df_en_cat = pd.DataFrame(encoder_cat, columns=cat_cols)

    df_final = pd.concat([df_num, df_en_cat], axis=1)
    df_final = df_final.reindex(columns=cols, fill_value=0)

    result = model.predict(df_final)[0]
    print(f" === {model} === ")
    print(f" === 운동타입 : {workout} === ")
    print(f" === 예상 Max HR : {max_hr:.2f} === ")
    print(f" === 예상 Min HR : {min_hr:.2f} === ")
    print(f" === 총 소모칼로리 예측 결과 : {result:.2f} === ")
    return f"{result:.2f}"
