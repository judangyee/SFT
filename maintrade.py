from pdb import pm
from pybit import HTTP
import pandas as pd
import time 
import datetime
import matplotlib.pyplot as plt
from prophet import Prophet
import datetime

while True:
    now = datetime.datetime.now()
    today = datetime.datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        second=0
    )
    delta = datetime.timedelta(hours=-3)
    dt = today + delta 
    from_time = time.mktime(dt.timetuple())

    session = HTTP(
        endpoint="https://api.bybit.com", 
        spot=False
    )

    resp = session.query_kline(
        symbol="BTCUSDT",
        interval="1",
        limit=200,
        from_time=from_time
    )

    result = resp['result']
    df = pd.DataFrame(result)
    df = df[['open_time', 'open', 'high', 'low', 'close']]


    change = pd.DataFrame()
    change['ds'] = df['open_time']
    change['y'] = ((df['close']-df['open'])/df['open'])*100
    sec = now.second

    # 변화율에대한 정규화
    for i in change.values.tolist():
        if i[1] >= 0.5: #0.5% 이상
            change.replace(1)
        elif -0.5 < i[1] < 0.5: #-0.5%미만 0.5%초과
            change.replace(0)
        elif i[1] <= -0.5: #-0.5% 이하
            change.replace(-1)
        else:
            print("Error") 
    change['ds'] = pd.to_datetime(change['ds'], unit='s') #epochtime을 datetime으로 변환

    # Prophet 사용 설정
    m = Prophet(changepoint_prior_scale=0.05)
    m.fit(change)

    future = m.make_future_dataframe(periods=1)
    future.tail()

    forecast = m.predict(future)
    Pchange = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

    cd = Pchange.tail(n=1) # 1분뒤 예측 값

    # 주문 시작
    if sec == 0:
        if cd >= 1:
            CloseLong(session)
            print("롱 주문")
            if sec == 60:
                print("포지션을 청산합니다")
            else:
                print("1")
        elif cd == 0:
            print("대기")
        elif cd <= -1:
            CloseShort(session)
            print("숏 주문")
            if sec == 60:
                print("포지션을 청산합니다")
            else:
                print("2")
        else:
            print("3")
    else:
        print("4")


