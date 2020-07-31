import pandas as pd
import chardet
import math

class Data:
    def __init__(self):
        pass

    def get_country_options(self,options):
        out=[]
        options = sorted(options['Country'])
        for country in options:
            out.append({'label': country, 'value':country})

        return out


    
    def to_df(self,raw_data):
        result='[]'
        if(raw_data):
            result=pd.json_normalize(raw_data)
            result.set_index('name')
            
        return result
    
    def rename(self,df):
        result = df
        result.columns = ['Country', 'Total Cases', 'Total Deaths', 'Total Recovered'] 
        return result


    def conversion(self,df_i):
        df = df_i
        df['total_cases']=df['total_cases'].str.replace(",","")
        df = df.fillna(0)
        df['total_cases']=df['total_cases'].astype(int)
        df['t_cases_rank'] = round(df.total_cases.rank(pct=True, method = 'min')*100)

        df['total_deaths']=df['total_deaths'].str.replace(",","").replace(r'','0')
        df = df.fillna(0)
        df['total_deaths']=df['total_deaths'].astype(int)
        df['t_deaths_rank'] = round(df.total_deaths.rank(pct=True, method = 'min')*100)

        df['total_recovered']=df['total_recovered'].str.replace(",","").replace(r'N/A','0')
        df = df.fillna(0)
        df['total_recovered']=df['total_recovered'].astype(int)
        df['t_recovered_rank'] = round(df.total_recovered.rank(pct=True, method = 'min')*100)


        return df


    def find_encoding(self, file):
        with open(file, 'rb') as f:
            f_encoding = chardet.detect(f.read())
        return f_encoding['encoding']