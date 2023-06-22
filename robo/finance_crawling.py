import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from tqdm import tqdm
from sqlalchemy import create_engine
 
# 네이버 금융에서 종목 가격정보와 거래량을 가져오는 함수: get_price


def get_price(company_code, name):
    # count=1000에서 1000은 과거 1000영업일간의 데이터를 의미. 사용자가 조절 가능
    url = "https://fchart.stock.naver.com/sise.nhn?symbol={}&timeframe=day&count=1102&requestType=0".format(company_code)
    get_result = requests.get(url)
    bs_obj = BeautifulSoup(get_result.content, "html.parser")
    
    # information
    inf = bs_obj.select('item')
    columns = ['date', 'open' ,'high', 'low', 'close', 'volume']
    df_inf = pd.DataFrame([], columns = columns, index = range(len(inf)))
    
    data_list = [str(item['data']).split('|') for item in inf]
    df_inf = pd.DataFrame(data_list, columns=columns)
    
    df_inf['date'] = pd.to_datetime(df_inf['date']).dt.strftime('%Y-%m-%d')
    df_inf[['open' ,'high', 'low', 'close', 'volume']].astype(float)
    
    df_inf['code'] = company_code
    df_inf['name'] = name
    return df_inf


# # 삼성전자
# print(get_price('005930'))

# # 코스피
# print(get_price('KOSPI'))


import psycopg2

# PostgreSQL 데이터베이스에 연결
conn = psycopg2.connect(
    host="192.168.0.39",
    port="5432",
    database="postgres",
    user="postgres",
    password="1234"
)

# 커서 생성
cur = conn.cursor()

# SELECT 문 실행
cur.execute("SELECT 종목코드, 종목명 FROM kor_ticker")

# 결과 가져오기
rows = cur.fetchall()
company_codes = [item[0] for item in rows]
names = [item[1] for item in rows]

# 연결 종료
cur.close()
conn.close()


columns = ['date', 'open' ,'high', 'low', 'close', 'volume']
df_total = pd.DataFrame(columns = columns)

for i in tqdm(range(len(company_codes))):
    df = get_price(company_codes[i], names[i])
    df_total = pd.concat([df_total,df])

# DB 연결
engine = create_engine("postgresql://postgres:1234@192.168.0.39:5432/postgres")
df_total.to_sql(name = 'finance_data',
        con = engine,
        schema = 'public',
        if_exists = 'append',
        index = False
        )
