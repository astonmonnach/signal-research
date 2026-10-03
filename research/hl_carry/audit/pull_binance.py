"""Binance BTCUSDT USD-M perp 1h klines via public REST API, 2023-05-01 -> now."""
import requests, time, pandas as pd
from datetime import datetime, timezone
cur=int(datetime(2023,5,1,tzinfo=timezone.utc).timestamp()*1000); end=int(time.time()*1000); out=[]
while cur<end:
    d=requests.get('https://fapi.binance.com/fapi/v1/klines',params={'symbol':'BTCUSDT','interval':'1h','startTime':cur,'limit':1500},timeout=30).json()
    if not d: break
    out+=d; cur=d[-1][0]+3600*1000; time.sleep(0.2)
df=pd.DataFrame(out).iloc[:,:6]; df.columns=['t','o','h','l','c','v']
df=df.drop_duplicates('t'); df[['o','h','l','c','v']]=df[['o','h','l','c','v']].astype(float)
df['ts']=pd.to_datetime(df.t,unit='ms',utc=True); df.to_csv('binance_btcusdt_perp_1h.csv',index=False)
print(len(df),df.ts.min(),df.ts.max())
