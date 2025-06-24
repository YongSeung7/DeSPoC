import MySQLdb
from MySQLdb import Error

def insert_data(NeckAvg, NeckMin, NeckMax, TurtleCnt, BadPoseCnt, Rweight, Lweight, LlegCnt, RlegCnt, BendCnt, L_UnbalCnt, R_UnbalCnt, SitTime):
    try:
        # MariaDB에 연결
        # qwdqwdqwdqwdqw
        connection = MySQLdb.connect(
            host='localhost',      # 데이터베이스 서버 주소
            user='yssong',           # MariaDB 사용자 이름
            passwd=' ',# MariaDB 비밀번호
            db='DeSPoC'            # 데이터베이스 이름
        )

        # 커서 생성
        cursor = connection.cursor()

        # 데이터 삽입 쿼리
        insert_query = '''
        INSERT INTO MyData (NeckAvg, NeckMin, NeckMax, TurtleCnt, BadPoseCnt, Rweight, Lweight, LlegCnt, RlegCnt, BendCnt, L_UnbalCnt, R_UnbalCnt, SitTime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        
        # 쿼리 실행
        cursor.execute(insert_query, (NeckAvg, NeckMin, NeckMax, TurtleCnt, BadPoseCnt, Rweight, Lweight, LlegCnt, RlegCnt, BendCnt, L_UnbalCnt, R_UnbalCnt, SitTime))
        connection.commit()
        
        print("데이터가 성공적으로 삽입되었습니다!.")
        
        # 삽입된 데이터 확인
        select_query = 'SELECT * FROM MyData WHERE `id` = LAST_INSERT_ID();'
        cursor.execute(select_query)
        #rows = cursor.fetchall()
        last_row = cursor.fetchone()  # 마지막 행만 가져옴
        print("MyData 테이블 데이터:")
        #for row in rows:
        #    print(row)
        print(last_row)
    except Error as e:
        print(f"Error: {e}")

    finally:
        # 연결 종료
        if connection:
            cursor.close()
            connection.close()
            print("MariaDB 연결이 종료되었습니다.")


def get_neck_avg_data():
    # MariaDB에 연결
    connection = MySQLdb.connect(
        host='localhost',      # 데이터베이스 서버 주소
        user='yssong',         # MariaDB 사용자 이름
        passwd=' ',            # MariaDB 비밀번호
        db='DeSPoC'            # 데이터베이스 이름
    )
    
    try:
        with connection.cursor() as cursor:
            # NeckAvg 필드의 최근 7개 값 가져오기
            sql = "SELECT NeckAvg FROM MyData ORDER BY id DESC LIMIT 7"
            cursor.execute(sql)
            result = cursor.fetchall()
            neck_avg_values = [row[0] for row in result]
    finally:
        connection.close()
    
    return neck_avg_values

def get_bad_cnt_data():
    # MariaDB에 연결
    connection = MySQLdb.connect(
        host='localhost',
        user='yssong',
        passwd=' ',
        db='DeSPoC'
    )
    
    try:
        with connection.cursor() as cursor:
            # 각 필드의 최근 7개 값 가져오기
            sql = """
                SELECT LlegCnt, RlegCnt, L_UnbalCnt, R_UnbalCnt, BendCnt 
                FROM MyData ORDER BY id DESC LIMIT 7
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            fields_data = {
                'LlegCnt': [row[0] for row in result],
                'RlegCnt': [row[1] for row in result],
                'L_UnbalCnt': [row[2] for row in result],
                'R_UnbalCnt': [row[3] for row in result],
                'BendCnt': [row[4] for row in result]
            }
    finally:
        connection.close()
    
    return fields_data

def get_weight_data():
    # MariaDB에 연결
    connection = MySQLdb.connect(
        host='localhost',
        user='yssong',
        passwd=' ',
        db='DeSPoC'
    )
    
    try:
        with connection.cursor() as cursor:
            # Rweight와 Lweight 필드의 최근 7개 값 가져오기
            sql = """
                SELECT Rweight, Lweight 
                FROM MyData ORDER BY id DESC LIMIT 7
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            weight_data = {
                'Rweight': [row[0] for row in result],
                'Lweight': [row[1] for row in result]
            }
    finally:
        connection.close()
    
    return weight_data
