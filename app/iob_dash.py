import plotly.graph_objects as go 
import plotly.express as px
import mysql.connector as database
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import datetime
import pandas as pd
import logging
import os
import numpy



app = dash.Dash(__name__)
server = app.server


# logging
LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
logging.basicConfig(level=LOGLEVEL)

# DEFINE THE DATABASE CREDENTIALS
user =     os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
host =     os.environ.get('DB_HOST')
port =     os.environ.get('DB_PORT', 3306)
db =       os.environ.get('DB', "iobroker")

# connect to iobroker db
connection = database.connect(
    user=user,
    password=password,
    host=host,
    port=port,
    database=db)

default_alias=os.environ.get('DEFAULT_ALIAS','alias-counter-gas')

cursor = connection.cursor()

# get a few nice colors, enough for all years
named_colorscales = px.colors.sequential.Aggrnyl_r
named_colorscales.append(px.colors.sequential.Aggrnyl)

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
current_year = int(date.strftime("%Y"))


def get_conter_per_month(datapoint_name):
    result={}
    try:
      query = "SELECT year(FROM_UNIXTIME(substring(ts,1,10))) as year, month(FROM_UNIXTIME(substring(ts,1,10))) as month ,round(max(val)-min(val),0) as value FROM ts_number \
                    WHERE id = (select id from datapoints where name =%s) \
                    GROUP BY year(FROM_UNIXTIME(substring(ts,1,10))),month(FROM_UNIXTIME(substring(ts,1,10))) \
                    ORDER BY ts"
      cursor.execute(query,[datapoint_name])
      
      for (year, month, value) in cursor:
        if not result.get(year):
          result[year]=[None] * 12
          
        result[year][int(month-1)]=value      
      
      df=pd.DataFrame.from_dict(result)
      return df
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")

def avg_per_month(value_dict):
    df=pd.DataFrame.from_dict(value_dict)
    means=df.mean(axis=1)
    logging.debug(f"avg_per_month, means: {means}")
    return means


def get_years():
    #result=[]
    #try:
    #  query = "SELECT distinct (year(FROM_UNIXTIME(substring(ts,1,10)))) as year from ts_number WHERE id = (select id from datapoints where name  =%s)"
    #  cursor.execute(query, [datapoint_name])

    #  for (year,) in cursor:
    #    result.append(year)
    #  return result
    #
    #except database.Error as e:
    #  print(f"Error retrieving entry from database: {e}")
    years=list(range(2015, 1+int(current_year)))
    years.reverse()
    return years


def get_counter_alias():
    result=[]
    try:
      query = "SELECT name as counter from datapoints where name like 'alias-counter-%' order by name"
      cursor.execute(query)

      for (counter,) in cursor:
        result.append(counter)
      return result
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")


@app.callback(Output('alias_counter_graph', 'figure'),
              Input('alias_selector', 'value'),
              [Input('year_selector', 'value')])
def create_chart(alias_name,years):
   
  year_list=[]
  if type(years) == int:
    year_list.append(years)
  else:
    year_list=years
  year_list.sort()

  logging.debug(f"year-list: {year_list}")
  # axuis_name
   
  fig = go.Figure()
  data=get_conter_per_month(alias_name)
  avg=avg_per_month(data)
  print(f"avg: {avg}")
  # add data of year

  col_count=0
  for year in year_list:
    fig.add_trace(go.Bar(
        name=f"{year}",
        marker_color=named_colorscales[col_count],
        y=data[year]
    ))
    col_count+=1
  

  fig.add_trace(go.Bar(
      y=avg,
      name=f"average",
      marker_color='red',
  ))

  fig.update_xaxes(
    ticktext=["Jan","Feb","Mar","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"],
    tickvals=[0,1,2,3,4,5,6,7,8,9,10,11]
    
)

  fig.update_layout(legend_title_text='Verbrauch')
  fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
  return fig




# list of available counter(s)
alias_list=get_counter_alias()
year_list=(get_years())

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('Zählerstände visualisieren'),
                                 html.P('Visualising consumptions from meter values.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='alias_selector',
                                                      options=alias_list,
                                                      multi=False, 
                                                      value=alias_list[0],
                                                      style={'backgroundColor': '#1E1E1E'},
                                                      className='stockselector'
                                                      ),
                                         dcc.Dropdown(id='year_selector',
                                                      options=year_list,
                                                      multi=True, 
                                                      value=year_list[0],
                                                      style={'backgroundColor': '#1E1E1E'},
                                                      className='stockselector'
                                                      ),
                                     ],
                                     style={'color': '#1E1E1E'})
                                ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(
                                      id='alias_counter_graph',
                                      config={'displayModeBar': False},
                                      animate=True
                                  )

                             ])
                              ])
        ]

)


if __name__ == '__main__':

  app.run_server(debug=True, use_reloader=True)