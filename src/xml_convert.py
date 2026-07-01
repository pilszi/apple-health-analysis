import xml.etree.ElementTree as ET
import pandas as pd

file_path = "./static/data/apple_health_export/export.xml"

target_source = "정원필의 Apple Watch"

summaries = []
workouts = []
heart_rates = []

print(f"⏳ [{target_source}] 데이터만 필터링하여 스캔 시작...")
context = ET.iterparse(file_path, events=("end",))

for event, elem in context:
    # 1. 일별 요약 추출 (ActivitySummary는 기기 구분이 없으므로 그대로 수집)
    if elem.tag == "ActivitySummary":
        summaries.append(elem.attrib)
        # print("=== ActivitySummary 발견 ===")
        elem.clear()
        
    # 2. 운동 세션 추출 (지정한 애플워치 기록만)
    elif elem.tag == "Workout":
        if elem.attrib.get("sourceName") == target_source:
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
                    
            
            # 가공된 딕셔너리를 기존 바구니에 담기
            workouts.append(workout_data)
        # print("=== Workout 발견 ===")
        elem.clear()
        
    # 3. 상세 기록 추출 (지정한 애플워치 기록 + 심박수만)
    elif elem.tag == "Record":
        if (elem.attrib.get("sourceName") == target_source and 
            elem.attrib.get("type") == "HKQuantityTypeIdentifierHeartRate"):
            # print("=== HeartRate 발견 ===")
            # 후속 조인(Join)과 시각화를 위해 타임스탬프와 심박수 값만 정제해서 보관
            heart_rates.append({
                'heart_rate': float(elem.attrib.get('value')),
                'timestamp': elem.attrib.get('startDate'),
                'sourceName': elem.attrib.get('sourceName') # 확인용
            })        
        # 메모리 해제
        elem.clear()

# 데이터프레임 변환
df_summary = pd.DataFrame(summaries)
df_workout = pd.DataFrame(workouts)
df_hr = pd.DataFrame(heart_rates)

# 데이터프레임 별 불필요한 컬럼 제거
summary_cols = ["appleMoveTime", "appleMoveTimeGoal", "appleStandHours", "appleStandHoursGoal"]
workout_cols = ["sourceName", "sourceVersion", "device"]
hr_cols = ["sourceName"]

if not df_summary.empty:
    df_summary['date'] = pd.to_datetime(df_summary['dateComponents'], errors='coerce').dt.date
    df_summary_dr = df_summary.drop(columns=summary_cols, errors='ignore')
    print("=== ActivitySummary ===")

# 2. 운동 세션 정제 (타임존 정보가 포함된 시간을 판다스 시간 객체로 변환)
if not df_workout.empty:
    df_workout['startDate'] = pd.to_datetime(df_workout['startDate'], errors='coerce')
    df_workout['endDate'] = pd.to_datetime(df_workout['endDate'], errors='coerce')
    df_workout['date'] = df_workout['startDate'].dt.date  # 조인용 Key 컬럼 생성
    # 운동 타입 불필요 단어 제거
    df_workout["workoutActivityType"] = df_workout[
        "workoutActivityType"
    ].str.replace("HKWorkoutActivityType", "", regex=False)

    df_workout_dr = df_workout.drop(columns=workout_cols, errors='ignore')
    print("=== Workout ===")

# 3. 상세 심박수 정제
if not df_hr.empty:
    df_hr['timestamp'] = pd.to_datetime(df_hr['timestamp'], errors='coerce')
    df_hr['date'] = df_hr['timestamp'].dt.date
    df_hr_dr = df_hr.drop(columns=hr_cols, errors='ignore')
    print("=== HeartRate ===")

df_summary_dr.to_csv("./static/data/apple_health_export/summary.csv", index=False, encoding="utf-8-sig")
df_workout_dr.to_csv("./static/data/apple_health_export/workout.csv", index=False, encoding="utf-8-sig")
df_hr_dr.to_csv("./static/data/apple_health_export/hr.csv", index=False, encoding="utf-8-sig")

print("✅ 모든 날짜/시간 컬럼이 성공적으로 정제되었습니다.")
print(f"Summary 행수: {len(df_summary)} | Workout 행수: {len(df_workout)} | HR 행수: {len(df_hr)}")


