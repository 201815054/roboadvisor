from sqlalchemy import create_engine
import pandas as pd
import numpy as np

def main():
    # PostgreSQL 연결 정보 설정
    db_host = '192.168.0.41'  # 데이터베이스 호스트
    db_port = '5432'  # 데이터베이스 포트
    db_name = 'postgres'  # 데이터베이스 이름
    db_user = 'postgres'  # 데이터베이스 사용자 이름
    db_password = '1234'  # 데이터베이스 비밀번호

    engine = create_engine(f'postgresql://{db_name}:{db_password}@{db_host}:{db_port}/{db_user}')


    kor_fs_query = """
    SELECT *
    FROM kor_fs
    WHERE 공시구분 = 'q'
    AND 계정 IN ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액'); """

    kor_fs = pd.read_sql_query(kor_fs_query, engine)

    ticker_list_query = """
    SELECT *
    FROM kor_ticker
    WHERE 기준일 = (
        SELECT MAX(기준일)
        FROM kor_ticker
    )
    AND 종목구분 = '보통주';
    """
    ticker_list = pd.read_sql_query(ticker_list_query, engine)

    # TTM 구하기
    kor_fs = kor_fs.sort_values(['종목코드','계정','기준일'])
    kor_fs['ttm'] = kor_fs.groupby(['종목코드','계정'], as_index=False)['값'].rolling(
        window=4, min_periods=4
    ).sum()['값']

    # 자본은 평균구하기
    kor_fs['ttm'] = np.where(kor_fs['계정'] == '자본', kor_fs['ttm'] /4,
                            kor_fs['ttm'])
    
    kor_fs = kor_fs.groupby(['계정','종목코드']).tail(1)

    kor_fs_merge = kor_fs[['계정','종목코드','ttm']].merge(ticker_list[['종목코드','시가총액','기준일']],on='종목코드')
    kor_fs_merge['시가총액'] = kor_fs_merge['시가총액'] / 100000000

    kor_fs_merge['value'] = kor_fs_merge['시가총액'] / kor_fs_merge['ttm']
    kor_fs_merge['value'] = kor_fs_merge['value'].round(4)
    kor_fs_merge['지표'] = np.where(
        kor_fs_merge['계정'] == '매출액','PSR',
        np.where(
            kor_fs_merge['계정'] == '영업활동으로인한현금흐름','PCR',
            np.where(kor_fs_merge['계정'] == '자본', 'PBR',
                    np.where(kor_fs_merge['계정'] == '당기순이익','PER', None))
        )
    )

    kor_fs_merge.rename(columns={'value':'값'},inplace=True)
    kor_fs_merge = kor_fs_merge[['종목코드','기준일','지표','값']]
    kor_fs_merge = kor_fs_merge.replace([np.inf,-np.inf, np.nan], None)

    kor_fs_merge[['종목코드','기준일','지표','값']].to_sql('kor_value', con=engine, if_exists='append',index=False)

if __name__ == '__main__':
    main()