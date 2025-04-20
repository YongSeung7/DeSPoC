from insert_db import insert_data
import time
from datetime import datetime

sit_time = datetime.strptime('01:30:00', "%H:%M:%S").time()
insert_data(
        NeckAvg=80.0,
        NeckMin=65.0,
        NeckMax=85.0,
        TurtleCnt=9,
        BadPoseCnt=100,
        Rweight=0.44,
        Lweight=0.56,
        LlegCnt=10,
        RlegCnt=20,
        BendCnt=100,
        L_UnbalCnt=80,
        R_UnbalCnt=90,
        SitTime=sit_time
    )
