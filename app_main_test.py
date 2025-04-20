import pandas as pd
import serial
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import csv
from insert_db import insert_data, get_neck_avg_data, get_bad_cnt_data, get_weight_data
from Arduino import Connect_Arduino
from flask import Flask, jsonify, render_template, request, url_for, redirect
import threading
import webbrowser  # 웹브라우저 모듈 추가


# PostureClassifier 모델 정의
class PostureClassifier(nn.Module):
    def __init__(self):
        super(PostureClassifier, self).__init__()
        # self.fc1 = nn.Linear(35, 128)
        # self.fc2 = nn.Linear(128, 64)
        # self.fc3 = nn.Linear(64, 32)
        # self.fc4 = nn.Linear(32, 7)
        self.fc1 = nn.Linear(35, 192)
        self.fc2 = nn.Linear(192, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 7)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x

# 모델 및 Scaler 로드
model = PostureClassifier()
model.load_state_dict(torch.load('optimized_posture_classifier.pth', map_location=torch.device('cpu')))
model.eval()
scaler = joblib.load('scaler.pkl')

# 자세 예측 함수
def predict_posture(new_data):
    new_data = scaler.transform([new_data])  # 데이터 표준화
    new_data_tensor = torch.tensor(new_data, dtype=torch.float32)
    with torch.no_grad():
        output = model(new_data_tensor)
        _, predicted = torch.max(output, 1)
        return predicted.item()


# 변수 초기화
sit_flag = end_flag = empty_flag = stretching_flag = stretching = stretching_flag_cnt = 0
turtle_count = 0
neck_max_value = neck_min_value = neck_average_value = 0.0
sit_time = empty_time = start_time = 0.0
L_weight = R_weight = R_ratio = L_ratio = R_ratio_avg = L_ratio_avg = 0.0
R_ratio_cnt = L_ratio_cnt = 0
cnt_badpose = cnt_Rleg = cnt_Lleg = cnt_Lub = cnt_Rub = cnt_bend = 0
init_flag = 1
data=[]
posture=['바른자세','왼쪽다리꼬기','오른쪽다리꼬기','좌측쏠림','우측쏠림','허리구부림']
predicted_posture =-1

# 아두이노 연결
ser_nano, ser = Connect_Arduino()

# 방석 센서 데이터 읽기 함수
def readsensor():
    timeout = time.time()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                data = line.split(',')
                data = [value for value in data if value]
                if len(data) == 35:
                    return [int(value) for value in data]
        if time.time() - timeout > 3:
            print('압력센서값을 읽어오지 못했습니다.')
            return [0] * 35

# DataFrame 생성
columns = [f's{i}' for i in range(35)]
df = pd.DataFrame([[1.0] * 35], columns=columns)

# 착석 상태 확인 함수
def check_sit():
    global sit_flag, start_time, empty_time, end_flag, empty_flag
    if empty_flag == 1:
        print('자리비움이 감지되어 다시 착석할때 까지 대기합니다.')
    else:
        print('DeSPoc에 착석해주세요.')
    empty_time = time.time()
    while True:
        data = readsensor()
        if sum(data) > 1200.0:
            sit_flag = 1
            empty_flag = 0
            start_time = time.time()
            print('착석이 인식되었습니다. 착석시간 측정을 시작합니다.')
            break
        if (time.time() - empty_time) >= 10:
            print('착석이 인식되지 않아 프로그램을 종료합니다.')
            empty_flag = 1
            end_flag = 1
            break


app = Flask(__name__)

@app.route('/get_data')
def get_data():
    global sit_time
    values = data
    
    right_values = data[16:33]
    left_values = data[0:5] + data[5:15] + data[33:]
    time_value = time.time() - start_time + sit_time

    web_data = {
        "values": values,
        "min": neck_min_value,
        "max": neck_max_value,
        "average": neck_average_value,
        "above_threshold": turtle_count,
        "right_values": right_values,
        "left_values": left_values,
        "right_average": R_ratio_avg,
        "left_average": L_ratio_avg,
        "empty_flag" : empty_flag,
        "time": time_value
    }
    return jsonify(web_data)


def sensor_loop():
    global sit_flag, end_flag, empty_flag, stretching_flag, stretching, stretching_flag_cnt
    global turtle_count, neck_max_value, neck_min_value, neck_average_value
    global sit_time, empty_time, start_time
    global L_weight, R_weight, R_ratio, L_ratio, R_ratio_avg, L_ratio_avg
    global R_ratio_cnt, L_ratio_cnt, cnt_badpose, cnt_Rleg, cnt_Lleg, cnt_Lub, cnt_Rub, cnt_bend
    global init_flag
    global data, posture, predicted_posture

# 기존의 main.py 
    check_sit()

    try:
        while True: 
            if end_flag == 1:
                raise KeyboardInterrupt

            data = readsensor()

            if sum(data) < 5.0:  #자리비움 체크
                sit_time += (time.time() - start_time)
                empty_flag = 1
                sit_flag = 0
                check_sit()

            #print("hello")

            # 자세 예측
            predicted_posture = predict_posture(data)
            # print(type(predicted_posture))
            # print(predicted_posture)
            if predicted_posture!=0:
                print(posture[predicted_posture])

            if predicted_posture == 1:
                cnt_Lleg += 1
            elif predicted_posture == 2:
                cnt_Rleg += 1
            elif predicted_posture == 3:
                cnt_Lub += 1
            elif predicted_posture == 4:
                cnt_Rub += 1
            elif predicted_posture == 5:
                cnt_bend += 1

            # 좌우 하중 비율 계산
            L_weight = sum(data[0:5]) + sum(data[5:15]) + sum(data[33:])
            R_weight = sum(data[16:33])
            if L_weight + R_weight != 0:
                R_ratio = R_weight / (L_weight + R_weight)
                R_ratio_cnt += 1
                R_ratio_avg = R_ratio_avg + (R_ratio - R_ratio_avg) / R_ratio_cnt
                L_ratio = L_weight / (L_weight + R_weight)
                L_ratio_cnt += 1
                L_ratio_avg = L_ratio_avg + (L_ratio - L_ratio_avg) / L_ratio_cnt

            # IMU 데이터 처리
            if ser_nano.in_waiting > 0:
                line = ser_nano.readline().decode('utf-8').rstrip()
                if "Pitch:" in line:
                    pitch = float(line.split(": ")[1])
                    if init_flag == 1:
                        neck_average_value = neck_max_value = neck_min_value = pitch
                        init_flag = 0
                    neck_average_value = (neck_average_value + pitch) / 2
                    neck_max_value = max(neck_max_value, pitch)
                    neck_min_value = min(neck_min_value, pitch)
                    if pitch < 68:
                        print("거북목 증상이 확인됩니다.")
                        turtle_count += 1
            # 스트레칭 시간 체크
            if (time.time() - start_time + sit_time)-(stretching_flag_cnt*5400)>5399 and (time.time() - start_time + sit_time)-(stretching_flag_cnt*5400)<5401:
                stretching_flag=1
                stretching_flag_cnt = stretching_flag_cnt + 1
                if stretching:
                    empty_flag=1
                    sit_flag=0
                else:
                    stretching_flag=0
            

    except KeyboardInterrupt:
        print("\n프로그램 종료")
        end_time = time.time()
        if empty_flag == 0:
            sit_time_str = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time + sit_time))
        else:
            sit_time_str = time.strftime("%H:%M:%S", time.gmtime(sit_time))

        cnt_badpose = cnt_bend + cnt_Lleg + cnt_Rleg + cnt_Lub + cnt_Rub
    
        sit_time = datetime.strptime(sit_time_str, "%H:%M:%S").time()

        print(f"거북목 증상이 확인된 횟수: {turtle_count}")

    finally:
        ser_nano.close()
        ser.close()
        insert_data(
            NeckAvg=neck_average_value,
            NeckMin=neck_min_value,
            NeckMax=neck_max_value,
            TurtleCnt=turtle_count,
            BadPoseCnt=cnt_badpose,
            Rweight=R_ratio_avg,
            Lweight=L_ratio_avg,
            LlegCnt=cnt_Lleg,
            RlegCnt=cnt_Rleg,
            BendCnt=cnt_bend,
            L_UnbalCnt=cnt_Lub,
            R_UnbalCnt=cnt_Rub,
            SitTime=sit_time)

# 메인 페이지 라우팅
@app.route('/')
def index():
    return render_template('index.html',time="time")

@app.route('/_current-posture')
def current_posture():
    return render_template('current_posture.html')

# Database 페이지
@app.route('/_database')
def database():
    neck_avg_data = get_neck_avg_data()
    fields_data = get_bad_cnt_data()
    weight_data = get_weight_data()
    return render_template('mariadb.html', neck_avg_data=neck_avg_data, fields_data=fields_data, weight_data=weight_data)

@app.route('/end_program', methods=['POST'])
def end_program():
    global end_flag
    data = request.get_json()
    end_flag = data.get('end_flag', 0)
    print("Program End Flag:", end_flag)
    return jsonify({"status": "success"}), 200

# Video 페이지
@app.route('/_video')
def video():
    return render_template('video.html')
# 고정된 데이터 제공 API

@app.route('/get_posture_data')
def get_posture_data(): #압력센서 35개 데이터 보냄
    md_data=[]
    md_data+=data
    md_data.append(predicted_posture)
    return jsonify(md_data)

def run_flask():
    app.run(host='192.168.137.175', port=9000)

# Flask와 무한 루프를 병렬로 실행
if __name__ == '__main__':
    # 각 작업을 스레드로 실행
    flask_thread = threading.Thread(target=run_flask)
    sensor_thread = threading.Thread(target=sensor_loop)

    # 두 스레드를 시작
    flask_thread.start()
    sensor_thread.start()

    # 두 스레드가 종료될 때까지 대기
    flask_thread.join()
    sensor_thread.join()