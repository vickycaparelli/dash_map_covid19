import pandas as pd
import chardet
import secrets
from main_scraper import Conector


class DataHandler:
    def __init__(self, api_conector):
        self.api_conector = api_conector
        self.country_data = self.get_country_data()
        self.country_options = self.get_country_options()

    def get_country_options(self):

        out=[{'label': country, 'value':country} for country in self.country_data['name']]

        return out

    @staticmethod
    def to_df(raw_data):
        result='[]'
        if(raw_data):
            result=pd.json_normalize(raw_data)
            result.set_index('name')
            
        return result

    def get_country_data(self):
        return DataHandler.to_df(self.api_conector.get_country_data_all())
    
    @staticmethod
    def rename(df):
        result = df
        result.columns = ['Country', 'Total Cases', 'Total Deaths', 'Total Recovered'] 
        return result

    @staticmethod
    def conversion(df):
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

    @staticmethod
    def find_encoding(file):
        with open(file, 'rb') as f:
            f_encoding = chardet.detect(f.read())
        return f_encoding['encoding']