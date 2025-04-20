import serial
import time

def Connect_Arduino():
    # 포트와 보드레이트 설정
    arduino_nano_port = '/dev/ttyACM0'  # 시스템에 맞게 포트 조정
    baud_rate_nano = 9600  # Arduino의 보드레이트와 동일하게 설정

    # 시리얼 연결 초기화
    ser_nano = serial.Serial(arduino_nano_port, baud_rate_nano, timeout=1)
    time.sleep(2)  # Arduino 초기화 대기
    print("거북목센서와 시리얼통신이 연결되었습니다.")
    
    SERIAL_PORT = '/dev/ttyACM1' 
    BAUD_RATE = 115200
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Arduino 초기화 대기
    print("압력센서와 시리얼통신이 연결되었습니다.")
    
    return ser_nano, ser  # 시리얼 객체들을 반환하여 이후 통신에 사용 가능