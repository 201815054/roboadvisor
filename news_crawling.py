import pandas as pd
import datetime
from tqdm import tqdm
import requests
import re
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import multiprocessing
import functools

'''
naver news 크롤링
'''

# date 설정
def set_date(start_date, end_date):
    dates = []

    start_date = datetime.date(*start_date)
    end_date = datetime.date(*end_date)

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        dates.append(date_str)
        current_date += datetime.timedelta(days=1)

    return dates


def save_titles(date, field, page):
    url = f'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={field}&sid1=101&date={date}&page={page}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    title_elements = soup.select('.list_body.newsflash_body ul li dl dt:not(.photo) a')
    titles = [element.text for element in title_elements]

    return titles


def preprocess_text(text):
    # 한글, 영문, 숫자, 공백을 제외한 모든 문자 제거
    text = re.sub('[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s\[\]\.]+', '', text)
    text = re.sub(r'[^\w\s\[\],\'"]+', '', text)

    # , ' " 제거
    text = re.sub(r'[\[\],\'"]+', '', text)
    # \n 제거
    text = text.replace('\n', '')
    # 연속된 공백을 하나의 공백으로 치환
    text = re.sub('\s+', ' ', text)
    # 양쪽 공백 제거
    text = text.strip()

    return text

def save_titles_wrapper(date, field, page):
    return save_titles(date, field, page)

def run(start_date, end_date, field):
    df = pd.DataFrame(columns=['field', 'date', 'title'])
    dates = set_date(start_date, end_date)

    try:
        for key, field_value in field.items():
            pool = multiprocessing.Pool()
            key_dates  = []
            key_titles = []

            for date in tqdm(dates, desc=key):
                partial_save_titles = functools.partial(save_titles_wrapper, date, field_value)
                results = pool.map(partial_save_titles, list(range(1, 30)))
                
                titles = [title for result in results for title in result]  # 모든 페이지의 기사 제목을 하나의 리스트로 병합
                key_dates.extend([date] * len(titles))
                key_titles.extend(titles)
            pool.close()
            pool.join()

            key_df  = pd.DataFrame({'title':key_titles})
            key_df ['date'] = key_dates
            key_df ['field'] = key
            key_df ['title'] = key_df ['title'].apply(preprocess_text)

            df = pd.concat([df, key_df], ignore_index=True)

    except Exception as e:
        print(e)

    return df.drop_duplicates(subset=['field','title'])



if __name__ == "__main__":

    economy = {'금융':259, '증권':258, '산업/재계':261, '중기/벤처':771, '부동산':260, '글로벌 경제':262, '생활경제':310, '경제일반':263}

    df = run([2023,1,1], [2023,5,31], economy)
    print(df)

    engine = create_engine("postgresql://postgres:1234@192.168.0.39:5432/postgres")
    df.to_sql(name = 'news',
            con = engine,
            schema = 'public',
            if_exists = 'append',
            index = False
            )
