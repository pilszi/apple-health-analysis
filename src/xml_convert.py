import xml.etree.ElementTree as ET
import pandas as pd

# Apple Watch Health data 중 필요한 data 만 정제

def convert_xml():
    """
        xml 파일에서 특정 attrib 만 추출하여 csv 파일로 저장하는 함수
    """
    file_path = "./static/data/apple_health_export/export.xml"
    workouts = []
    heart_rates = []
    result = 0  
    try:
        context = ET.iterparse(file_path, events=("end",))
        print(f"⏳ [Apple Watch] 데이터만 필터링하여 스캔 시작...")
        for event, elem in context:

            # 1. 운동 세션 추출 (지정한 애플워치 기록만)
            if elem.tag == "Workout":
                if "Apple Watch" in elem.attrib.get("sourceName"):
                # if elem.attrib.get("sourceName") == target_source:
                    workout_data = dict(elem.attrib)
                    
                    # 자식 요소(MetadataEntry)들을 순회하면서 HKAverageMETs 검색
                    for child in elem:
                        if child.tag == "WorkoutStatistics":
                            # 'key'가 아니라 'type' 속성을 확인해야 합니다.
                            stat_type = child.attrib.get("type")
                            
                            if stat_type == "HKQuantityTypeIdentifierActiveEnergyBurned":
                                # 'value'가 아니라 'sum' 속성에서 가져옵니다.
                                sum_value = child.attrib.get("sum")
                                if sum_value:
                                    try:
                                        # 이미 숫자 형식 문자열이므로 바로 float 변환이 가능합니다.
                                        workout_data["ActiveEnergyBurned"] = float(sum_value)
                                    except ValueError:
                                        workout_data["ActiveEnergyBurned"] = sum_value
                                        
                            elif stat_type == "HKQuantityTypeIdentifierBasalEnergyBurned":
                                sum_value = child.attrib.get("sum")
                                if sum_value:
                                    try:
                                        workout_data["BasalEnergyBurned"] = float(sum_value)
                                    except ValueError:
                                        workout_data["BasalEnergyBurned"] = sum_value
                        elif child.tag == "MetadataEntry":
                            meta_key = child.attrib.get("key")
                            if meta_key == "HKWeatherTemperature":
                                key_value = child.attrib.get("value")
                                if key_value:
                                    # workout_data["Temperature"] = float(key_value)
                                    workout_data['Temperature'] = workout_data['Temperature'].astype(str).str.replace(r'[^-0-9.]', '', regex=True)
                                else:
                                    # workout_data['Temperature'] = float(workout_data['Temperature']).interpolate(method='linear')
                                    workout_data['Temperature'] = ""

                            elif meta_key ==  "HKWeatherHumidity":
                                key_value = child.attrib.get("value")
                                if key_value:
                                    # workout_data["Humidity"] = float(key_value)
                                    workout_data['Humidity'] = workout_data['Humidity'].astype(str).str.replace(r'[^-0-9.]', '', regex=True)
                                else:
                                    #  workout_data['Humidity'] = float(workout_data['Humidity']).interpolate(method='linear')
                                     workout_data['Humidity'] = ""
                    
                    # 가공된 딕셔너리를 기존 바구니에 담기
                    workouts.append(workout_data)
                elem.clear()
                # print("=== Workout 발견 ===")

            # 2. 상세 기록 추출 (지정한 애플워치 기록 + 심박수만)
            elif elem.tag == "Record":
                if ("Apple Watch" in elem.attrib.get("sourceName") and 
                    elem.attrib.get("type") == "HKQuantityTypeIdentifierHeartRate"):
                    # 후속 조인(Join)과 시각화를 위해 타임스탬프와 심박수 값만 정제해서 보관
                    heart_rates.append({
                        'heart_rate': float(elem.attrib.get('value')),
                        'timestamp': elem.attrib.get('startDate'),
                        'sourceName': elem.attrib.get('sourceName') # 확인용
                    })
        
                # 메모리 해제
                    # print("=== HeartRate 발견 ===")
                elem.clear()

        # 데이터프레임 변환
        df_workout = pd.DataFrame(workouts)
        df_hr = pd.DataFrame(heart_rates)

        workout_cols = ["sourceName", "sourceVersion", "device", "durationUnit", "creationDate"]
        hr_cols = ["sourceName"]

        # 2. 운동 세션 정제 (타임존 정보가 포함된 시간을 판다스 시간 객체로 변환)
        if not df_workout.empty:
            df_workout['startDate'] = pd.to_datetime(df_workout['startDate'], errors='coerce')
            df_workout['endDate'] = pd.to_datetime(df_workout['endDate'], errors='coerce')
            df_workout['date'] = df_workout['startDate'].dt.date  # 조인용 Key 컬럼 생성
            # 운동 타입 불필요 단어 제거
            df_workout["workoutActivityType"] = df_workout[
                "workoutActivityType"
            ].str.replace("HKWorkoutActivityType", "", regex=False)
            # workoutActivityType 컬럼 값 불필요한 반복 단어 제거
            df_workout["workoutActivityType"] = df_workout["workoutActivityType"].str.replace("HKWorkoutActivityType", "", regex=False)
            # 데이터프레임 별 불필요한 컬럼 제거
            df_workout_dr = df_workout.drop(columns=workout_cols, errors='ignore')
            print("=== Workout ===")
            df_workout_dr.to_csv("./static/data/apple_health_export/workout.csv", index=False, encoding="utf-8-sig")

        # 3. 상세 심박수 정제
        if not df_hr.empty:
            df_hr['timestamp'] = pd.to_datetime(df_hr['timestamp'], errors='coerce')
            df_hr['date'] = df_hr['timestamp'].dt.date
            df_hr_dr = df_hr.drop(columns=hr_cols, errors='ignore')
            print("=== HeartRate ===")
            df_hr_dr.to_csv("./static/data/apple_health_export/hr.csv", index=False, encoding="utf-8-sig")
        
        result = 1

        print("✅ 모든 날짜/시간 컬럼이 성공적으로 정제되었습니다.")
        print(f"Workout 행수: {len(df_workout)} | HR 행수: {len(df_hr)}")
    except FileNotFoundError as f:
        print(f"파일을 찾지 못했습니다 : {f}")
    # except Exception as e:
    #     print(f"기타 에러 발생 : {e}")

    return {"result": result}




