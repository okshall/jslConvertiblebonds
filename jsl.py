import requests
import csv
from operator import itemgetter
import pandas as pd

database=[]
#构造英文pool便于获取所需的value
keyPool_en=['bond_id','bond_nm','price','increase_rt','stock_nm','sprice',
            'sincrease_rt','pb','convert_price','convert_value','premium_rt','rating_cd',
            'put_convert_price','force_redeem_price','convert_amt_ratio','maturity_dt','year_left','curr_iss_amt','ytm_rt',
            'ytm_rt_tax','volume','dblow','convert_cd']
#构造中文pool
keyPool_zh=['代码','转债名称','现价','涨跌幅','正股名称','正股价',
            '正股涨跌','PB','转股价','转股价值','溢价率','评级',
            '回售触发价','强赎触发价','转债占比','到期时间','剩余年限','剩余规模','到期税前收益',
            '到期税后收益','成交额','双低','转股状态']
def get_jsl_kzz():
    url="https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t=1577251762134"#从Headers的请求URL中获取
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    response=requests.get(url,headers=headers)
    json=response.json()
    for one in json['rows'] :
        cell=one['cell']
        if cell['price_tips']=='待上市':
            continue #筛选掉未上市的股票
        data_dict = {}
        data_dict.fromkeys(keyPool_zh)
        for key,value in cell.items():
            if key in keyPool_en:
                data_dict[keyPool_zh[keyPool_en.index(key)]]=value
        
        if 'EB' in data_dict['转债名称'] :
            continue;
        if 'ST' in data_dict['正股名称'] :
            continue;
        database.append(data_dict)
    return pd.DataFrame(database)

df = get_jsl_kzz()

#剔除PB小于1
df = df[df['PB'].astype('float') > 1]

df = df[df['PB'].astype('float') < 5]

#剔除成交额小于100万
df = df[df['成交额'].astype('float') > 100]
#剔除价格大于115
df = df[df['现价'].astype('float') < 115]
#剔除溢价率大于20%
df = df[(df['溢价率'].str.strip("%").astype('float')/100) < 0.2]
#剔除剩余年限小于1
df = df[df['剩余年限'].astype('float') > 1]
#剔除剩余规模小于5千万
df = df[df['剩余规模'].astype('float') > 0.5]
#剔除未到转股期
df = df[df['转股状态'] != '未到转股期']
#剔除到期税前收益率小于0
df = df[(df['到期税后收益'].str.strip("%").astype('float')/100) > 0]
print(df)

writer = pd.ExcelWriter("test.xls")
df.to_excel(writer, 'all')
writer.save()
print('over')
