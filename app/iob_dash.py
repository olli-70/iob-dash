import plotly.graph_objects as go
import mysql.connector as database
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import datetime
import pandas as pd
import logging
import os

# logging
LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
logging.basicConfig(level=LOGLEVEL)

# DEFINE THE DATABASE CREDENTIALS
user =     os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
host =     os.environ.get('DB_HOST')
port =     os.environ.get('DB_PORT', 3306)
db =       os.environ.get('DB', "iobroker")

# dict of months
month = {	'1':'Jan',
		      '2':'Feb',
		      '3':'Mar',
		      '4':'Apr',
		      '5':'May',
		      '6':'Jun',
		      '7':'Jul',
		      '8':'Aug',
		      '9':'Sep',
		      '10':'Oct',
		      '11':'Nov',
		      '12':'Dec'	}

# connect to iobroker db
connection = database.connect(
    user=user,
    password=password,
    host=host,
    port=port,
    database=db)



cursor = connection.cursor()

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
current_year = int(date.strftime("%Y"))


def get_conter_per_month(datapoint_name,years):

    # make sure that years is a list and convert it to string
    years_select=[]
    if type(years) == int:
      years_select=[str(years)]
    else:
      years_select=years

    # all available years
    years_available=list(range(2015, 1+int(current_year)))

    try:
      query = f"SELECT max(date(FROM_UNIXTIME(substring(ts,1,10)))) as date, round(max(val)-min(val),0) as value FROM ts_number \
                    WHERE id = (select id from datapoints where name =\"{datapoint_name}\") and \
                    year(FROM_UNIXTIME(substring(ts,1,10))) in ({','.join(str(item) for item in years_available)})  \
                    GROUP BY year(FROM_UNIXTIME(substring(ts,1,10))),month(FROM_UNIXTIME(substring(ts,1,10))) \
                    ORDER BY ts"
      df = pd.read_sql(query, con = connection)
      df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
      df_per_month=df.set_index([df.date.dt.month, df.date.dt.year]).value.unstack()
      means=df_per_month.mean(axis=1)
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")
    
    try:
      query = f"SELECT max(date(FROM_UNIXTIME(substring(ts,1,10)))) as date, round(max(val)-min(val),0) as value FROM ts_number \
                    WHERE id = (select id from datapoints where name =\"{datapoint_name}\") and \
                    year(FROM_UNIXTIME(substring(ts,1,10))) in ({','.join(str(item) for item in years_select)})  \
                    GROUP BY year(FROM_UNIXTIME(substring(ts,1,10))),month(FROM_UNIXTIME(substring(ts,1,10))) \
                    ORDER BY ts"
      df = pd.read_sql(query, con = connection)
      df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
      df_per_month=df.set_index([df.date.dt.month, df.date.dt.year]).value.unstack()
      return df_per_month,means
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")

def avg_per_month(df):
    means=df.mean(axis=1)
    return means

def get_years():
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

  
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

@app.callback(Output('alias_counter_graph', 'figure'),
              Input('alias_selector', 'value'),
              [Input('year_selector', 'value')])
def create_chart(alias_name,years):
   
  # convert year_selector values to sorted list

  fig = go.Figure()
  
  df_monthly_values,avg=get_conter_per_month(alias_name,years)
  logging.debug(f"df 1: \n{df_monthly_values}")
  # add the data columns as bar rows for each year

  for y in df_monthly_values:
    dfy=df_monthly_values[y]
    x_val=[]
    for nr in list(dfy.index.values):
      x_val.append(month[str(nr)])
    fig.add_bar(x = x_val, y = list(df_monthly_values[y]), name = str(y))

  # add the average as last bar row
  for nr in list(avg.index.values):
      x_val.append(month[str(nr)])
  fig.add_bar(x = x_val, y = list(avg), name = 'avg')

  fig.update_layout(legend_title_text='Verbrauch')
  fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
  
  
  
  return fig

# list of available counter(s)
alias_list=get_counter_alias()
year_list=(get_years())

alias_list_items=[]
for counter in alias_list:
   item=dbc.DropdownMenuItem(counter)
   alias_list_items.append(item)

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Jahre"),
                dcc.Dropdown(
                    id="year_selector",
                    options=year_list,
                    value=year_list[0],
                    multi=True, 
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Messwerte"),
                dcc.Dropdown(
                    id="alias_selector",
                    
                    options=alias_list,
                    value=alias_list[0],
                ),
            ]
        ),
        
    ],
    body=True,
)

app.layout = dbc.Container(
    [
        html.H1("IOBroker Auswertungen"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(dcc.Graph(id="alias_counter_graph"),  md=8),
                
            ],
            align="center",
        ),
    ],
    fluid=True,
)

server = app.server










if __name__ == '__main__':

  app.run_server(debug=True, use_reloader=True)