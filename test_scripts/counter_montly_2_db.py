import mysql.connector as database
import json
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

def get_conter_per_month(datapoint_name,year):
    result=[0,0,0,0,0,0,0,0,0,0,0,0]
    try:
      query = "SELECT month(FROM_UNIXTIME(substring(ts,1,10))) as month ,round(max(val)-min(val),0) as value FROM ts_number \
                    WHERE id = (select id from datapoints where name =%s) and \
                    year(FROM_UNIXTIME(substring(ts,1,10)))=%s \
                    GROUP BY year(FROM_UNIXTIME(substring(ts,1,10))),month(FROM_UNIXTIME(substring(ts,1,10))) \
                    ORDER BY ts"
      cursor.execute(query,[datapoint_name, year])
      
      for (month, value) in cursor:
        result[int(month-1)]=value
        #print(f"Successfully retrieved {month}, {value}")
      
      #print(f"Result: {result}")
      return result
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")

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

def add_data(data):
    
    try:
      query = "REPLACE into counter_per_month (counter_alias, _year, january, february, march, april, may, june, july,august, september, october, november, december) \
                   values \
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
      cursor.execute(query,data)
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")



def get_start_year(datapoint_name):
    result=[]
    try:
      query = "SELECT min(year(FROM_UNIXTIME(substring(ts,1,10)))) as year from ts_number WHERE id = (select id from datapoints where name =%s)"
      cursor.execute(query,[datapoint_name])
      result=cursor.fetchone()[0]
      return int(result)
    
    except database.Error as e:
      print(f"Error retrieving entry from database: {e}")




if __name__ == '__main__':
  yearly_consumption={}
  
  # get current date

  currentDateTime = datetime.datetime.now()
  date = currentDateTime.date()
  current_year = int(date.strftime("%Y"))
   

  counter_aliases=get_counter_alias()
   #
  for alias_name in counter_aliases:
      print(f"conter: {alias_name}")
      for y in range(get_start_year(alias_name),current_year+1):
         data=[alias_name, y]
         data.extend(get_conter_per_month(alias_name,y))
         add_data(data)
         print(f"data: {data}")
         
  #print(json.dumps(yearly_consumption))
   
    

    
 