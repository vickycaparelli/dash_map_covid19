import requests
import json


class Conector:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key 
        }
        self.data = self.get_data()
        self.last_date = self.get_last_run_date()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params= self.params)
        self.data = json.loads(response.text)
        return self.data

    def get_total_cases(self):
        data = self.data['total']

        for content in data:
            if content['name'] == 'Coronavirus Cases:':
                return content['value']
        return "0"
    
    def get_total_deaths(self):
        data = self.data['total']

        for content in data:
            if content['name'] == 'Deaths:':
                return content['value']
        return "0"
        
    def get_total_recovered(self):
        data = self.data['total']

        for content in data:
            if content['name'] == 'Recovered:':
                return content['value']
        return "0"
    
    def get_country_data(self, country):
        data = self.data['country']

        for content in data:
            if content['name'].lower() == country.lower():
                return content
        return 0
    
    def get_country_data_all(self):
        return self.data['country']

    def get_country_list(self):
        out_list = []
        for country in self.data['country']:
            out_list.append(country['name'])
        return out_list

    def get_last_run_date(self):
        response_pj = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}', params= self.params)
        resppj_json = json.loads(response_pj.text)

        RUN_TOKEN = resppj_json['last_ready_run']['run_token']
        response_run = requests.get(f'https://www.parsehub.com/api/v2/runs/{RUN_TOKEN}', params= self.params)
        resrun_json = json.loads(response_run.text)
        self.last_date = resrun_json['end_time'].replace('T',' ')
        return self.last_date
        

