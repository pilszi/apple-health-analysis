import xml.etree.ElementTree as ET
import pandas as pd

# Apple Watch Health data 중 필요한 data 만 정제

def convert_xml():
    """
        xml 파일에서 특정 attrib 만 추출하여 csv 파일로 저장하는 함수
    """
    try:
        file_path = "./static/data/apple_health_export/export.xml"
        workouts = []
        heart_rates = []
        result = 0  
        context = ET.iterparse(file_path, events=("end",))
        try:
            print(f"[Apple Watch] 데이터만 필터링하여 스캔 시작...")
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
                                        value = "".join(v for v in key_value if v.isdigit() or v in ['.', '-'])
                                        # 화씨로 저장된 온도 섭씨로 변환
                                        workout_data["Temperature"] = (float(value) - 32) / 1.8
                                    else:
                                        workout_data["Temperature"] = None

                                elif meta_key ==  "HKWeatherHumidity":
                                    key_value = child.attrib.get("value")
                                    if key_value:
                                        value = "".join(v for v in key_value if v.isdigit() or v in ['.', '-'])
                                        # 저장된 습도 값은 5600 %  같이 100이 곱해진 값
                                        workout_data["Humidity"] = float(value) / 100
                                    else:
                                        workout_data["Humidity"] = None
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
                            'startDate': elem.attrib.get('startDate'),
                            'sourceName': elem.attrib.get('sourceName') # 확인용
                        })
            
                    # 메모리 해제
                        # print("=== HeartRate 발견 ===")
                    elem.clear()
        except KeyError as k:
            print(f"key 가 틀렸습니다. : {k}")
        except SyntaxError as s:
            print(f"문법 오류 : {s}")
        except Exception as e:
            print(f"기타 에러 발생 : {e}")

        # 추출한 데이터 정리 후 csv 파일로 저장
        try:    
            # 데이터프레임 변환
            df_workout = pd.DataFrame(workouts)
            df_hr = pd.DataFrame(heart_rates)

            workout_cols = ["sourceName", "sourceVersion", "device", "durationUnit", "creationDate"]
            hr_cols = ["sourceName"]

            # 3. 운동 세션 컬럼 정리
            if not df_workout.empty:
                df_workout["startDate"] = pd.to_datetime(df_workout["startDate"], format='mixed', errors='coerce').dt.tz_localize(None)
                df_workout["endDate"] = pd.to_datetime(df_workout["endDate"], format='mixed', errors='coerce').dt.tz_localize(None)
                df_workout["date"] = df_workout["startDate"].dt.date
                df_workout['duration'] = df_workout['duration'].astype(float).round(3)
                # 운동 타입 불필요 단어 제거
                df_workout["workoutActivityType"] = df_workout[
                    "workoutActivityType"
                ].str.replace("HKWorkoutActivityType", "", regex=False)
                
                # workoutActivityType 컬럼 값 불필요한 반복 단어 제거
                df_workout["workoutActivityType"] = df_workout["workoutActivityType"].str.replace("HKWorkoutActivityType", "", regex=False)
                # 데이터프레임 별 불필요한 컬럼 제거
                df_workout = df_workout.drop(columns=workout_cols, errors='ignore')
                print("=== Workout ===")
                df_workout.to_csv("./static/data/apple_health_export/workout.csv", index=False, encoding="utf-8-sig")

            # 4. 심박수 데이터 컬럼 정리
            if not df_hr.empty:
                df_hr['startDate'] = pd.to_datetime(df_hr['startDate'], format='mixed', errors='coerce').dt.tz_localize(None)
                df_hr['date'] = df_hr['startDate'].dt.date
                df_hr['heart_rate'] = df_hr['heart_rate'].astype(float).round(3)
                df_hr = df_hr.drop(columns=hr_cols, errors='ignore')
                print("=== HeartRate ===")
                df_hr.to_csv("./static/data/apple_health_export/hr.csv", index=False, encoding="utf-8-sig")
            print(f"Workout 행수: {len(df_workout)} | HR 행수: {len(df_hr)}")
        except KeyError as k:
            print(f"key 가 틀렸습니다. : {k}")
        except SyntaxError as s:
            print(f"문법 오류 : {s}")
        except Exception as e:
            print(f"기타 에러 발생 : {e}")
        result = 1

    except FileNotFoundError as f:
        print(f'파일을 찾지 못했습니다. : {f}')

    return {"result": result}
