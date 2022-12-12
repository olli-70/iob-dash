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




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])


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

default_alias=os.environ.get('DEFAULT_ALIAS','alias-counter-gas')

cursor = connection.cursor()

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
current_year = int(date.strftime("%Y"))


def get_conter_per_month(datapoint_name,years):

    # make sure that years is a list and convert it to string
    years_string=""
    if type(years) == int:
      years_string=str(years)
    else:
      years_string=','.join(str(item) for item in years)

    try:
      query = f"SELECT max(date(FROM_UNIXTIME(substring(ts,1,10)))) as date, round(max(val)-min(val),0) as value FROM ts_number \
                    WHERE id = (select id from datapoints where name =\"{datapoint_name}\") and \
                    year(FROM_UNIXTIME(substring(ts,1,10))) in ({years_string})  \
                    GROUP BY year(FROM_UNIXTIME(substring(ts,1,10))),month(FROM_UNIXTIME(substring(ts,1,10))) \
                    ORDER BY ts"
      df = pd.read_sql(query, con = connection)
      df['date'] = pd.to_datetime(df.date, format='%Y-%m-%d')
      df_per_month=df.set_index([df.date.dt.month, df.date.dt.year]).value.unstack()
      return df_per_month
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")


def avg_per_month(df):
    means=df.mean(axis=1)
    logging.debug(f"avg_per_month, means: \n{means}")
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
   
  # convert year_selector values to sorted list

  fig = go.Figure()
  
  df_monthly_values=get_conter_per_month(alias_name,years)
  avg=avg_per_month(df_monthly_values)
  
  # add data of year

  print(f"df_monthly_values {df_monthly_values}")

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

print(alias_list_items)


app.layout = dbc.Container( (
  [
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('Zählerstände visualisieren'),
                                 html.P('Visualising consumptions from meter values.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dbc.DropdownMenu(
                                          label="Zaehler",
                                          children=alias_list,
                                      ),   

                                         dcc.Dropdown(id='alias_selector',
                                                      options=alias_list,
                                                      multi=False, 
                                                      value=alias_list[0],
                                                      
                                                      
                                                      ),
                                         dcc.Dropdown(id='year_selector',
                                                      options=year_list,
                                                      multi=True, 
                                                      value=year_list[0],
                                                  
                                                      
                                                      ),
                                        dcc.Graph(
                                                     id='alias_counter_graph',
                                                     config={'displayModeBar': False},
                                                     animate=True
                                                    )
                                     ],
                                     )
                                ]
                             ),
                    
                              ])
                          
        ]

))


if __name__ == '__main__':

  app.run_server(debug=True, use_reloader=True)