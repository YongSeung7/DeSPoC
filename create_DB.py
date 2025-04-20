import MySQLdb
from MySQLdb import Error

try:
    # MariaDB에 연결
    connection = MySQLdb.connect(
        host='localhost',      # 데이터베이스 서버 주소
        user='yssong',           # MariaDB 사용자 이름
        passwd=' ',# MariaDB 비밀번호
        db='DeSPoC'            # 데이터베이스 이름
    )

    # 커서 생성
    cursor = connection.cursor()

    # 테이블 생성 쿼리
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS MyData (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `DateTime` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `NeckAvg` FLOAT,
        `NeckMin` FLOAT,
        `NeckMax` FLOAT,
        `TurtleCnt` INT,
        `BadPoseCnt` INT,
        `Rweight` FLOAT,
        `Lweight` FLOAT,
        `LlegCnt` INT,
        `RlegCnt` INT,
        `BendCnt` INT,
        `L_UnbalCnt` INT,
        `R_UnbalCnt` INT,
        `SitTime` TIME
    ) AUTO_INCREMENT=1;
    '''
    
    # 쿼리 실행
    cursor.execute(create_table_query)
    connection.commit()
    
    print("Test 테이블이 성공적으로 생성되었습니다.")

except Error as e:
    print(f"Error: {e}")

finally:
    # 연결 종료
    if connection:
        cursor.close()
        connection.close()
        print("MariaDB 연결이 종료되었습니다.")
