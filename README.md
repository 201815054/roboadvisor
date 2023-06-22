# roboadvisor

----- 테이블 설명 ------
- 테이블 이름 : news
  - 설명: 네이버 경제 뉴스
  - 날짜: 2019 ~ 2023(~5월)
  - 칼럼:
    - field : 분야 (금융, 증권, 산업/재계, 중기/벤처, 부동산, 글로벌 경제, 생활경제, 경제일반)
    - date : 날짜 (ex) 20230101)   
    - title : 뉴스 기사 제목

<!-- <<<<<<< chan -->

- 테이블 이름 : finance_basic
  - 설명: krx 기본 지표 
  - 날짜: 2019 ~ 2023
  - 컬럼:
    - Date : 기준일
    - Adj Close : 종가
    - ticker : 종목코드
    - MarketCap : 시가총액
    
  <!-- - 설명: krx 기본 지표
  - 날짜: 2019 ~ 2023
  - 컬럼:
    - itemcode : 종목코드
    - item_name : 종목명
    - market_classification : 시장구분
    - closing_price : 종가
    - market_capitalization : 시가총액
    - base_date : 기준일
    - contrast : 대비
    - fluctuation_rate : 등락률
    - industry_name : 업종명
    - item_classification : 종목구분 (ex) 코스피, 코스닥) -->


<!-- >>>>>>> main -->

- 테이블이름 : kor_ticker
  - 설명: KOSDAQ , KOSPI 상장기업 종목코드 (비상장기업포함)
  - 날짜: (기준일) 2023-06-14
  - 컬럼: 
    - 종목코드 : 6자리 종목코드 
    - 종목명 : 종목명
    - 시장구분 : KOSPI, KOSDAQ
    - 종가 : 종가
    - 시가총액 : 시가총액
    - 기준일 : 시장기준일(상장종목)
    - eps : 주당순이익(순이익 / 보통주의 총수) 주식 시장에서 EPS가 높을수록 기업의 수익성이 좋다고 간주함
    - 선행eps : 현재 시점에서 예상되는 미래의 주당순이익 , 기업의 실제 공시된 재무데이터와는 다를수도있음
    - bps : 기업의 주당순자산 가치 (부채를제외한순자산/ 보통주의 총 수)
    - 주당배당금 : 기업이 발행한 주식 한 주당 지급하는 배당금
    - 종목구분 : 보통주,우선주(우선적으로 배당받는 권리를 가짐) 


- 테이블이름 : kor_fs
  - 설명: 종목별 재무제표 (KOSDAQ,KOSPI) 
  - 날짜: 연기(2020~2022) , 분기(2022) 
  - 컬럼:
    - 계정 : 포괄손익계산서항목(매출액,영업이익,당기순이익 등) , 재무상태표(자산,부채,자본), 현금흐름표(영업활동으로인한현금흐름,투자활동으로인한현금흐름,재무활동으로인한현금흐름 등)
    - 기준일: 연기(2020~2022) , 분기(2022)
    - 값 : 계정에 따른 값(단위: 억원)
    - 종목코드 : 종목코드
    - 공시구분 :y(연기), q(분기)


- 테이블이름 : kor_value 
  - 설명: kor_fs 분기데이터의 가치지표 
  - 날짜: 202206 ~ 202303  
  - 컬럼:
    - 종목코드: 종목코드
    - 기준일: ticker 시장기준일
    - 지표 : 가치지표(PBR,PCR,PSR,PER)
    - 값 : 가치지표값

