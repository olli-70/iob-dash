import pandas as pd
import numpy as np
import calendar

df = pd.DataFrame(
         dict(date=pd.date_range('2013-01-01', periods=42, freq='M'),
              pb=np.random.rand(42)))

print (df)

df2=df.set_index([df.date.dt.month, df.date.dt.year]).pb.unstack()
df2['date'] = df2['date'].apply(lambda x: calendar.month_abbr[x])
print (df2)