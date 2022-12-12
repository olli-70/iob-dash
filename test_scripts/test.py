import pandas as pd
import mysql.connector as database
import datetime
import os





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
x_val=["Ja","Fe","Ma","Ap","Ma","Ju","Jul","Au","Se","Ok","No","De"]



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
      print(f"Dataframe: {df}")
      return result
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")

def avg_per_month(value_dict,year):
    df=pd.DataFrame.from_dict(value_dict)
    df2=df.drop([year], axis=1)
    print(df2)
    means=df2.mean(axis=1)
    return means.to_dict()
    

if __name__ == '__main__':
  currentDateTime = datetime.datetime.now()
  date = currentDateTime.date()
  current_year = int(date.strftime("%Y"))

  monthly_values=get_conter_per_month('alias-counter-gas')
  year_list=monthly_values.keys()
  print(f"Keys: {year_list}")
  average_values=avg_per_month(monthly_values,2022)
  print(f"Durchschnittswerte: {average_values}")
  
  


