import plotly   
import plotly.express as px

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
from datetime import datetime
import secrets
from data import Data
from main_scraper import Conector
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

PAGE_SIZE = 10

d = Data()
c = Conector(secrets.API_KEY,secrets.PROJECT_TOKEN)
df_data = d.to_df(c.get_country_data_all())
df_localization = pd.read_csv('geo_data.csv', sep = ';', encoding=d.find_encoding('geo_data.csv'))

df = pd.merge(df_localization, df_data, how='left', left_on='Country', right_on='name')
df['total_cases']=df['total_cases'].str.replace(",","")
df = df.fillna(0)
df['total_cases']=df['total_cases'].astype(int)



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
     html.Div(
        className="head",
         children=[
            html.H1(children='Coronavirus (Covid19) - Global Cases Graphs'),
            html.P(children='COVID-19 is the infectious disease caused by the most recently discovered coronavirus. This disease was unknown before the outbreak began in Wuhan, China, in December 2019 and now is a pandemic affecting many countries.'),
            html.P(children='Track how it is spreading around the globe with up-to-date visuals.'), 
            html.Br(),
            html.P(className="source",
                    children=['Data source: Coronavirus COVID-19 Global Cases by ', html.A('wordometers.info', href='https://www.worldometers.info/coronavirus/')]),
            html.P(className="source",
                    children=['Last updated: ', c.last_date, ' UTC +0000'])
         ]
     ),

     html.Div(
         className="wrapper", 
         children=[
            html.Div(className="deaths", children=[html.H3('Total Deaths'),
                                html.H5(c.get_total_deaths())]),
            html.Div(className="total", children=[html.H3('Total Cases'),
                                html.H5(c.get_total_cases())]),
            html.Div(className="recovered", children=[html.H3('Total Recovered'),
                                html.H5(c.get_total_recovered())])
         ]),
     html.Div(className="component-graph",children=[
          dcc.Graph(id='the_graph')
     ]),
     html.Div(className="components",children=[dash_table.DataTable(
        id='datatable-paging',
        columns=[{"name": i, "id": i} for i in sorted(df_data.columns)],
        style_as_list_view=True,
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom'
        )
        ]),
    html.Br()
 ])


@app.callback(
     [Output('datatable-paging', 'data'),
     Output(component_id='the_graph', component_property='figure')],
     [Input('datatable-paging', "page_current"),
      Input('datatable-paging', "page_size")])


def update_table(page_current,page_size):

    fig = px.choropleth(df, locations="ISO3_code",
         color="total_cases",
         hover_name="Country", # column to add to hover information
         color_continuous_scale=px.colors.sequential.OrRd)
    
    
    return (df_data.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records'), fig)

if __name__ == '__main__':
     app.run_server(debug=True)
