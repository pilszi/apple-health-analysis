from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os

from main import hello

app = FastAPI()

class TaskModel(BaseModel):
    task: str

@app.get("/run-script")
def run_script():
    
    try:
        result = hello()
        # 스크립트가 print() 등으로 출력한 결과물(stdout)을 반환
        return {"result": f"스크립트 실행 성공! 출력 결과: {result}"}
    
    except subprocess.CalledProcessError as e:
        return {"result": f"스크립트 실행 실패: {e.stderr.strip()}"}