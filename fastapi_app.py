from fastapi import FastAPI

from src.preprocessing import PreProcess
from src.xml_convert import convert_xml
from src.final_pre import pre_ml_data
from src.corr import correlation_df
from src.train_test import ml_train_test_split, ml_train
from src.predict import predict_calories, model_5, cols, encoder, model_6, model_7, model_8, model_9, model_10, model_11, model_12, model_13, model_14
from db import insert_oracle

app = FastAPI()



@app.get("/convert")
def run_script():
    result = convert_xml()
    return {"result": result}


@app.get("/preprocess")
def preprocess():
    """
        csv 파일 전처리 요청
        (결측치, 중복값, 불필요한 데이터 삭제)
    """
    result = PreProcess()
    return {"result": result}


@app.get("/final_pre")
def final_pre():
    """
        머신러닝 학습을 위한 데이터 최종 정리
    """
    result = pre_ml_data()
    return {"result": result}

@app.get("/corr")
def correlation():
    """
        데이터들 간에 상관관계 분석 요청
    """
    result = correlation_df()
    return {"result": result}


@app.get("/ml_train")
def train():
    """
        머신러닝 학습 요청
    """
    x_train, x_test, y_train, y_test = ml_train_test_split()
    result = ml_train(x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test)
    return {"result": result}


@app.post("/predict")
def predict(data:dict):
    """
        학습된 모델에 데이터 예측
    """
    res_dict = {}
    for i in range(5, 15):
        model = globals().get(f"model_{i}")
        result = predict_calories(avg_hr=data["avg_hr"], workout=data["workout"], duration=data["duration"], model=model, cols=cols, encoder=encoder)
        res_dict[f'{result["model"]}'] = result["result"]
    
    return {"result": res_dict}

@app.post('/db')
def db(data:dict):
    insert_oracle(data)
    return 'OK!'