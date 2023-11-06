
import requests
import pandas as pd
# from datetime import datetime
import datetime
import sqlite3
import FinanceDataReader as fdr 
import pandas_datareader as pdr
import talib as ta
from matplotlib import pyplot as plt

from zipfile import ZipFile



# df = fdr.DataReader('005930', '2020')

# print(df)

# 한국거래소에 상장된 종목의 가격 데이터 가져오기


def update_code():      # 주식 코드 다운로드
    print("주식 코드 로드 시작")
    kospi_stocks = fdr.StockListing('kospi')
    kosdaq_stocks = fdr.StockListing('kosdaq')

    stocks_data = pd.concat([kospi_stocks, kosdaq_stocks], ignore_index=True)       # 코스피, 코스닥 합치기
    stock_code_name = stocks_data[['Name', 'Code']]
    
    stock_code_name.to_excel('code_name.xlsx', sheet_name='코드데이터', index=False)
    
    print("주식 코드 로드 완료")
    
def load_codeNname():        # 주식 코드 가져오기
    df = pd.read_excel('code_name.xlsx')
    return df
    

def download_stock_data():
    start_time = datetime.datetime.now()

    code_data = load_codeNname()    
    codes = code_data['Code']
    names = code_data['Name']

    conn = sqlite3.connect('stock_data.db')

    for i, stock_code in enumerate(codes):
        df = pdr.naver.NaverDailyReader(stock_code, start='2013-01-01').read()       
        

        stock_name = names[i]

        total_stock_count = len(codes)
        print(f'{i}/{total_stock_count} : {stock_name}')
        df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)       # 데이터를 숫자형태로 변경
        # 한열은 이런식으로 가능하다. df['a'] = pd.to_numeric(df['a'])

        df['Change'] = df['Close'].diff()
        try:        # 첫 상장 종목에 오류가 생길수 있음
            df['Change_R'] = round(df['Close'].pct_change() * 100, 2)
        except:
            df['Change_R'] = 0

        df.to_sql(stock_name, conn, index=True, if_exists='replace')
    conn.close

    end_time = datetime.datetime.now()
    spend_time = end_time - start_time
    print(f'걸린시간은 {spend_time}')

    print("완료")

def get_test_data():            # 테스트 데이터 추출
    conn = sqlite3.connect('stock_data.db')
    # cursor = conn.cursor()          # cursor를 사용하는 방법

    # cursor.execute('SELECT * FROM 삼성전자 WHERE strftime("%Y", "Date") >= "2022"; ')   # 23년 이후 값만 뽑기
    # result = cursor.fetchall()
    # columns = ['Date','Open', 'High', 'Low', 'Close', 'Volume']
    # df = pd.DataFrame(result, columns=columns)       # Dataframe 형식으로 바꿀 필요가 있음
    

    # read_sql_query 를 사용하는 방법
    sql_query = 'SELECT * FROM 삼성전자 WHERE strftime("%Y", "Date") >= "2022";'        # 23년 이후 값만 뽑기
    df = pd.read_sql_query(sql_query, conn)

    conn.close()
    return df

def get_min_price_last_100_days(price_list):        # 100일 최저가 구하기
    min_price_list = []
    data_size = len(price_list)
    
    if data_size < 100:
        min_price_list.extend([0]*data_size)
    else:
        for i in range(data_size):   
            
            if i < 99:          # 0부터 시작하므로 99이다.
                # print("여기")
                min_price_list.append(0)
                
            else:
                last_100_days_prices = price_list[0:100]  # 최근 100 거래일의 가격 데이터
                min_price = min(last_100_days_prices)  # 최저가 계산
                min_price_list.append(min_price)        
                price_list.pop(0)        # 리스트의 첫번째 수를 제거한다.                
    
    return min_price_list


def get_max_price_last_100_days(price_list):        # 100일 최고가 구하기
    max_price_list = []
    data_size = len(price_list)
    
    if data_size < 100:
        max_price_list.extend([0]*data_size)
    else:
        for i in range(data_size):   
            
            if i < 99:          # 0부터 시작하므로 99이다.
                # print("여기")
                max_price_list.append(0)
                
            else:
                last_100_days_prices = price_list[0:100]  # 최근 100 거래일의 가격 데이터
                max_price = max(last_100_days_prices)  # 최저가 계산
                max_price_list.append(max_price)        
                price_list.pop(0)        # 리스트의 첫번째 수를 제거한다.                
    
    return max_price_list


def crossover(data1, data2):    # data1이 data2를 위로 뚫고 올라갈 때, 데이터프레임 형식의 데이터를 받는다.

    prev_data1 = data1.shift()    
    subtraction1 = data1 - data2
    subtraction2 = prev_data1 - data2
    result = (subtraction1 > 0) & (subtraction2 < 0)      # 직전 데이터가 비교 값보다 작고 현재 데이터가 비교값보다 크다.

    return result    


def crossunder(data1, data2):    # data1이 data2를 아래로 뚫고 내려갈 때, 데이터프레임 형식의 데이터를 받는다.
    
    prev_data1 = data1.shift()    
    subtraction1 = data1 - data2
    subtraction2 = prev_data1 - data2
    result = (subtraction1 < 0) & (subtraction2 > 0)      # 직전 데이터가 비교 값보다 크고 현재 데이터가 비교값보다 작다.

    return result

def pivothigh(data, pre_period, next_period):
    length = len(data)
    result = []
    data = list(data)
    for i, price in enumerate(data):
        if i < pre_period + next_period:
            result.append(False)
        elif i >= pre_period + next_period:
            if max(max(data[i-(pre_period + next_period):i-next_period]), max(data[i-next_period:i])) <= data[i-next_period]:
                result.append(True)
            else:
                result.append(False)
        
    return result


def pivotlow(data, pre_period, next_period):
    length = len(data)
    result = []
    data = list(data)
    for i, price in enumerate(data):
        if i < pre_period + next_period:
            result.append(False)
        elif i >= pre_period + next_period:
            if min(min(data[i-(pre_period + next_period):i-next_period]), min(data[i-next_period:i])) >= data[i-next_period]:
                result.append(True)
            else:
                result.append(False)
        
    return result    

def percentrank(source, length):    # 데이터는 데이터프레임을 받는다. 주어진 시리즈의 현재값에 대해 더 작거나 같은 값의 퍼센트(봉 개수 기준임)
    percentrank_list = []
    sum_sub_zero_list = []

    data_size = len(source)

    if data_size < length:
        percentrank_list.extend([0]*data_size)
    else:
        for i in range(data_size):   
            
            if i < length:          
                # print("여기")
                percentrank_list.append(0)
                
            else:
                current_source = source[i]   # x 일 후의 데이터
                length_data = source[i:i+length]  # 최근 length 거래일의 데이터
                comparison_data = length_data - current_source
                
                sub_zero_data = comparison_data.where(comparison_data < 0, 1).where(comparison_data >= 0, 0)        # 0보다 작으면 1, 0보다 같거나 크면 1입력
                                
                sum_sub_zero = sub_zero_data.sum()
                sum_sub_zero_list.append(sum_sub_zero)
                percentrank_data = round((sum_sub_zero / length) * 100, 1)
                
                percentrank_list.append(percentrank_data)
    
    return percentrank_list


def dummy_data():

    data = {'이름': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
            '점수': [85, 92, 78, 95, 89]}
    df = pd.DataFrame(data)
    return df

# df['rank'] = df['close'].rank(ascending=False)  순위


def load_last_data():       # 가장 최근 주식데이터 하나만 로드
    
    code_name = pd.read_excel('code_name.xlsx')
    names = code_name['Name']    
    conn = sqlite3.connect('stock_data.db')

    df = pd.DataFrame()   
    
    for i, name in enumerate(names):
        sql_query = f'SELECT * FROM "{name}" ORDER BY Date DESC LIMIT 1;'        # 마지막 행 , LIMIT 1은 첫번째행 -여기서는 거꾸로 정렬해서 첫번째 행을 뽑는다. 이게 더 빠름        
        # sql_query = f'SELECT * FROM "{name}" WHERE Date = (SELECT MAX(Date) FROM "{name}");'        # 마지막 행 - 다른 방법

        new_df = pd.read_sql_query(sql_query, conn)
        new_df['Name'] = name
        df = pd.concat([df, new_df])
        
    conn.close()    
    return df


def get_today_data():       # 오늘 주식 다운로드
    
    start_time = datetime.datetime.now()
    print(f"시작시간 = {start_time}")

    df = pd.DataFrame()
    code_data = load_codeNname()    
    codes = code_data['Code']
    names = code_data['Name']
    
    yesterday = datetime.datetime.now()- datetime.timedelta(days=4)
    yesterday = yesterday.strftime("%Y-%m-%d")
    for i, stock_code in enumerate(codes):
        new_df = pdr.naver.NaverDailyReader(stock_code, start=yesterday).read()
        
        stock_name = names[i]
        total_stock_count = len(codes)
        print(f'{i+1}/{total_stock_count} : {stock_name}')
        new_df[['Open', 'High', 'Low', 'Close', 'Volume']] = new_df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)       # 데이터를 숫자형태로 변경
        # 한열은 이런식으로 가능하다. df['a'] = pd.to_numeric(df['a'])
        
        new_df['Change'] = new_df['Close'].diff()
        new_df['Change_R'] = round(new_df['Close'].pct_change() * 100, 2)
        new_df['Name'] = stock_name
        new_df = new_df.tail(1)
        df = pd.concat([df, new_df], ignore_index=True)

    df['Change_rank'] = df['Change_R'].rank(ascending=False)    
    df = df.sort_values(by='Change_rank', ascending=True)      # 오름차순 정렬
    end_time = datetime.datetime.now()
    time = end_time -start_time
    print(f'걸린시간 = {time}')
    
    return df



def test():
    # df = get_today_data()
    # # download_stock_data()
    # df = load_last_data()    
    df = get_test_data()    
    close = df['Close']
    
    a = pivothigh(close, 5, 5)
    df2 = pd.DataFrame()
    df2['Date'] = df['Date']
    df2['close'] = close
    df2['pivothigh'] = a
    df2.to_excel('test5.xlsx')
    
    # # high = df['High']
    # # df['yday_close'] = close.shift()
    # df = df.sort_values(by='Close', ascending=True)      # 오름차순 정렬
    # df.to_excel('test4.xlsx')
    
test()


def dart_jemu():        # 다트 공시 api 이용 더 공부 필요
    KEY = 'aa4c9f5eeebed570a0f8abb4ada0edeaef3c060c'
    url = 'https://opendart.fss.or.kr/api/corpCode.xml'
    params = {'crtfc_key' : KEY}

    respose = requests.get(url, params=params).content

# 참고 코드

# 3일 전 날짜 계산
## three_days_ago = now - datetime.timedelta(days=3)