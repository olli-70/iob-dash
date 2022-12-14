import plotly.graph_objects as go
import pandas as pd
import mysql.connector as database
import datetime
import os
import io

# DEFINE THE DATABASE CREDENTIALS
user =     os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
host =     os.environ.get('DB_HOST')
port =     os.environ.get('DB_PORT', 3306)
db =       os.environ.get('DB', "iobroker")

connection = database.connect(
    user=user,
    password=password,
    host=host,
    port=port,
    database=db)

cursor = connection.cursor()
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
    print(f"MEANS \n{list(means)}")
    return means
    

if __name__ == '__main__':
  currentDateTime = datetime.datetime.now()
  date = currentDateTime.date()
  current_year = int(date.strftime("%Y"))

  df_monthly_values=get_conter_per_month('alias-counter-gas',[2019,2020,2017,2018,2016,2015,2021])
  
  
  print(f"Monthly: \n----------\n{df_monthly_values}\n----------")
  print(f"Monthly: \n----------\n{avg_per_month(df_monthly_values)}\n----------")
  
  
    
    
  #
#
  #  
  #fig = go.Figure()
  #for y in df_monthly_values:
  #    dfy=df_monthly_values[y]
  #    print(list(df_monthly_values[y]))
  #    x_val=[]
  #    
  #    for nr in list(dfy.index.values):
  #      x_val.append(month[str(nr)])
  #    
  #    fig.add_bar(x = x_val, y = list(df_monthly_values[y]), name = str(y))
  #
  #fig.show()