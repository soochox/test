
import requests
import pandas as pd
# from datetime import datetime
import datetime
import sqlite3
import FinanceDataReader as fdr 
import pandas_datareader as pdr


def load_codeNname():        # 주식 코드 가져오기
    df = pd.read_excel('code_name.xlsx')
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
        try:
            new_df['Change_R'] = round(new_df['Close'].pct_change() * 100, 2)
        except:
            new_df['Change_R'] = 0
            

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
    df = get_today_data()
    df.to_excel('test5.xlsx')
    
test()
input("작업이 완료되었습니다. 엔터를 누르면 창을 닫습니다.")
