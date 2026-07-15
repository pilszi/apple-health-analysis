import oracledb

user = "system"
pw = "1234"
host = "localhost:1521/xe"

def insert_oracle(df):
    """
        oracle DB 저장하는 함수
    """
    con = None

    sql = """INSERT INTO apple_health(
                id, workout_date, workoutactivitytype, duration, 
                workout_avg_hr, workout_max_hr, workout_min_hr, training_load, totalenergyburned
            )VALUES(
                apple_health_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8
            )"""
    
    insert_data = df[["date", "workoutActivityType", 
                      "duration", "workout_avg_hr", 
                      "workout_max_hr", "workout_min_hr", 
                      "training_load", "totalenergyburned"]]
    try:
        con = oracledb.connect(
            user= user,
            password= pw,
            dsn= host,
        )
        print("==== 접속완료 ====")
        with con.cursor() as cur:
            cur.executemany(sql, insert_data)
        con.commit()
        print("==== apple_health 저장 완료 ====")
    except Exception as e:
        print(f'에러 발생 : {e}')
        if con:
            con.rollback()
    finally:
        if con:
            con.close()
    return "Insert OK!"



def con():
    conn = oracledb.connect(
            user= user,
            password= pw,
            dsn=host,
        )
    print("접속완료")
    return conn

