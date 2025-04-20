import serial
import csv
import time

# 시리얼 포트 설정 (Arduino가 연결된 포트를 설정)
SERIAL_PORT = '/dev/ttyACM0'  # Windows의 경우. Mac이나 Linux는 '/dev/ttyUSB0'와 같은 형식
BAUD_RATE = 115200

# CSV 파일 설정
CSV_FILENAME = 'sensor_data.csv'

# 시리얼 포트 열기
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # 시리얼 포트 안정화 대기

print(f"시리얼 포트 {SERIAL_PORT}에서 데이터를 수신 중...")

# CSV 파일 열기 및 데이터 저장
with open(CSV_FILENAME, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([f'Channel {i}' for i in range(35)])  # 헤더 작성

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    # 데이터를 ','로 구분하여 리스트로 변환 후 CSV에 저장
                    data = line.split(',')
                    data = [value for value in data if value]
                    if len(data) == 35:  # 32개의 채널 데이터가 모두 있는지 확인
                        writer.writerow(data)
                        print(f"{SERIAL_PORT}: {data}")  # 콘솔에 출력
    except KeyboardInterrupt:
        print("데이터 수집 종료")
    finally:
        ser.close()
