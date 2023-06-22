# 전종목 재무제표 크롤링
from sqlalchemy import create_engine
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import re 
from tqdm import tqdm
import psycopg2
import os

def main():
    # DB연결 
    engine = create_engine('postgresql://postgres:1234@192.168.0.39:5432/postgres')


    # PostgreSQL 연결 정보 설정
    db_host = '192.168.0.39'  # 데이터베이스 호스트
    db_port = '5432'  # 데이터베이스 포트
    db_name = 'postgres'  # 데이터베이스 이름
    db_user = 'postgres'  # 데이터베이스 사용자 이름
    db_password = '1234'  # 데이터베이스 비밀번호

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    mycursor = conn.cursor()

    # 기준일 기준 국내 종목(kospi, kosdaq) ticker 가져오기 
    tk_query = 'kor_ticker'
    tk_query = f"SELECT * FROM {tk_query}"
    #데이터프레임으로 변환
    df = pd.read_sql_query(tk_query,conn)
    ticker_list = df['종목코드'].tolist()

    # 오류 발생시 저장할 리스트 
    error_list = []

    # 재무제표 클렌징 함수
    def clean_fs(df,ticker,frequency):

        df = df[~df.loc[:,~df.columns.isin(['계정'])].isna().all(axis=1)]
        df = df.drop_duplicates(['계정'],keep='first')
        df = pd.melt(df, id_vars='계정',var_name='기준일',value_name='값')
        df = df[~pd.isnull(df['값'])]
        df['계정'] = df['계정'].replace({"계산에 참여한 계정 펼치기": ""},regex = True)
        df['기준일'] = pd.to_datetime(df['기준일'],
                                format='%Y-%m') + pd.tseries.offsets.MonthEnd()
        df['종목코드'] = ticker
        df['공시구분'] = frequency

        return df 

    data_fs_bind = pd.DataFrame()
    for i in tqdm(range(0,len(ticker_list))): # 종목별로 csv저장 
        # 티커선택
        ticker = ticker_list[i]
        print(ticker)
        try:
            url = f'https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=N&ReportGB=D&NewMenuID=103&stkGb=701'
            # 데이터 받아오기
            data = pd.read_html(url, displayed_only=False)

            # 연간 데이터
            data_fs_y = pd.concat([
                data[0].iloc[:,~data[0].columns.str.contains('전년동기')],data[2],
                data[4]
            ])
            data_fs_y = data_fs_y.rename(columns={data_fs_y.columns[0]: "계정"})

            # 결산년 찾기
            page_data = rq.get(url)
            page_data_html = BeautifulSoup(page_data.content, "html.parser")

            fiscal_data = page_data_html.select('div.corp_group1 > h2')
            fiscal_data_text = fiscal_data[1].text
            fiscal_data_text = re.findall('[0-9]+',fiscal_data_text)

            # 결산년에 해당하는 계정만 남기기
            data_fs_y = data_fs_y.loc[:, (data_fs_y.columns =='계정') | (
                data_fs_y.columns.str[-2:].isin(fiscal_data_text))]
            
            # 클렌징 
            data_fs_y_clean = clean_fs(data_fs_y,ticker,'y')

            # 분기 데이터
            data_fs_q = pd.concat([
                data[1].iloc[:, ~data[1].columns.str.contains('전년동기')], data[3],
                data[5]
            ])
            data_fs_q = data_fs_q.rename(columns={data_fs_q.columns[0]:"계정"})

            data_fs_q_clean = clean_fs(data_fs_q, ticker,'q')

            # 두개 합치기 
            # data_fs_bind = pd.concat([data_fs_bind, data_fs_y_clean, data_fs_q_clean])
            data_fs_bind = pd.concat([data_fs_y_clean, data_fs_q_clean])
            data_fs_bind.to_csv(f'./{ticker}.csv')

        except:
            #오류 발생시 해당 종목명 저장 및 다음루프로 이동
            print(ticker)
            error_list.append(ticker)

            
    # db 데이터 삽입
    path = './'
    file_list = os.listdir(path)
    file_list_py = [file for file in file_list if file.endswith('.csv')] ## 파일명 끝이 .csv인 경우
    print(len(file_list_py))
    for i in tqdm(file_list_py): # 저장한 종목별 csv파일을 한개씩 db에 저장 
        data = pd.read_csv(path + i)
        data.to_sql('kor_fs', con=engine, if_exists='append',index=False)

    engine.dispose()
    conn.close()            

if __name__ == '__main__':
    main()