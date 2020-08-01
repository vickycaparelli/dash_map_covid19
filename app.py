import plotly   
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import secrets
from data import Data
from main_scraper import Conector



d = Data()
c = Conector(secrets.API_KEY,secrets.PROJECT_TOKEN)

df_data = d.to_df(c.get_country_data_all())
df_localization = pd.read_csv('geo_data.csv', sep = ';', encoding=d.find_encoding('geo_data.csv'))

df = pd.merge(df_localization, df_data, how='left', left_on='Country', right_on='name')
df = d.conversion(df)
df_data = d.rename(df_data)

fig_sun_deaths =  px.sunburst(
                         data_frame=df,
                         path=["Continent", 'Country'],  # Root, branches, leaves  
                         color="total_deaths",
                         color_continuous_scale=px.colors.diverging.Picnic)

fig_sun_cases =  px.sunburst(
                         data_frame=df,
                         path=["Continent", 'Country'],  # Root, branches, leaves  
                         values="total_cases",
                         color_discrete_sequence=px.colors.qualitative.Safe)

fig_sun_recovered =  px.sunburst(
                         data_frame=df,
                         path=["Continent", 'Country'],  # Root, branches, leaves  
                         color="total_recovered",
                         color_continuous_scale=px.colors.sequential.haline)

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(children=[
     html.Div(
        className="head",
         children=[
            html.H1(children='Coronavirus (Covid19) - Global Cases Graphs'),
            html.P(className="par", children='COVID-19 is the infectious disease caused by the most recently discovered coronavirus. This disease was unknown before the outbreak began in Wuhan, China, in December 2019 and now is a pandemic affecting many countries.'),
            html.P(className="par", children='Track how it is spreading around the globe with up-to-date visuals.'), 
            html.Br(),
            html.P(children=['Data sources: COVID-19 global cases by ', html.A('wordometers.info', href='https://www.worldometers.info/coronavirus/'),
                               ', ISO codes used for geolocalization and world population data were extracted from ', 
                               html.A('Wikipedia.org - ISO Codes', href='https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes'),"/",
                               html.A('Wikipedia.org - Pop Data', href='https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'),]),
            html.P(children=['Last updated: ', c.last_date, ' UTC +0000'])
         ]
     ),

     html.Div(
         className="wrapper", 
         children=[
            html.Div(className="deaths", children=[html.H2('Total Deaths'),
                                html.H4(c.get_total_deaths())]),
            html.Div(className="total", children=[html.H2('Total Cases'),
                                html.H4(c.get_total_cases())]),
            html.Div(className="recovered", children=[html.H2('Total Recovered'),
                                html.H4(c.get_total_recovered())])
         ]),
    html.Div(id = 'cont-sunburst', className='wrapper', children = [
          dcc.Graph(id = "sun-plot-tdeaths",
                    figure = fig_sun_deaths),
          dcc.Graph(id = "sun-plot-tcases",
                    figure = fig_sun_cases),
          dcc.Graph(id = "sun-plot-trecovered",
                    figure = fig_sun_recovered)
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
        page_size=13,
        page_action='custom'
        )
        ]),
        html.Div(className='dropdown-text', 
                    children = [
                                html.H3("Select a country to find out how it was affected by the disease"),
                                dcc.Dropdown(id='dropdown',
                                             options=d.get_country_options(df),
                                             value='USA',
                                             clearable=False
                                ),
                                html.P("The following summary exhibits how this country was affected by COVID-19 in comparison with the rest countries of the world."),
                                html.P("The percentile represents the percentage of countries with less cases than the selected one. [Per millon of habitants. Separated in 3 categories (dead, recovered, confirmed)]")                
        ]),
    html.Div(id = 'container-out')
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


@app.callback(
     Output('container-out', 'children'),
     [Input('dropdown', "value")])


def update_drop(value):
     return_divs=[]
     filter_rank = df[df['Country']==value]

     if((filter_rank['total_cases']==0).bool()):
         filter_rank['total_cases']="Not Reported"
         filter_rank['t_cases_rank']="-"
     else:
          filter_rank['total_cases'] = filter_rank['total_cases'].apply('{:,}'.format)
    
     if((filter_rank['total_deaths']==0).bool()):
         filter_rank['total_deaths']="Not Reported"
         filter_rank['t_deaths_rank']="-"
     else:
          filter_rank['total_deaths'] = filter_rank['total_deaths'].apply('{:,}'.format)
    
     if((filter_rank['total_recovered']==0).bool()):
         filter_rank['total_recovered']="Not Reported"
         filter_rank['t_recovered_rank']="-"
     else:
          filter_rank['total_recovered'] = filter_rank['total_recovered'].apply('{:,}'.format)
    
     return_divs.append(html.Div(className="wrapper-drop", children=[
               html.Div(className="deaths", children=[html.H2('Total Deaths'),
                                   html.H4(filter_rank['total_deaths'])]),
               html.Div(className="total", children=[html.H2('Total Cases'),
                                   html.H4(filter_rank['total_cases'])]),
               html.Div(className="recovered", children=[html.H2('Total Recovered'),
                                   html.H4(filter_rank['total_recovered'])]),
               html.Div(className="deaths", children=[html.H3('Total Deaths - Percentile (th)'),
                                   html.H5(filter_rank['t_deaths_rank']) ] ),
               html.Div(className="total", children=[html.H3('Total Cases - Percentile (th)'),
                                   html.H5(filter_rank['t_cases_rank'])]),
               html.Div(className="recovered", children=[html.H3('Total Recovered - Percentile (th)'),
                                   html.H5(filter_rank['t_recovered_rank']) ] ),
     ]) )
     
     return return_divs

if __name__ == '__main__':
     app.run_server(debug=True)
