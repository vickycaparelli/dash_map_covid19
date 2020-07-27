import pandas as pd
import chardet

class Data:
    def __init__(self):
        pass

    def get_country_options(self,options):
        out=[]
        options = sorted(options)
        for country in options:
            out.append({'label': country, 'value':country})

        return out

    
    def to_df(self,raw_data):
        result='[]'
        if(raw_data):
            result=pd.json_normalize(raw_data)
            result.set_index('name')
        return result
    

    def find_encoding(self, file):
        with open(file, 'rb') as f:
            f_encoding = chardet.detect(f.read())
        return f_encoding['encoding']