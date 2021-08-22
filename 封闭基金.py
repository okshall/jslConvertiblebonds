import requests
from operator import itemgetter
import pandas as pd
import xalpha as xa
import operator
from datetime import datetime

def get_pd_data(url, keyPool_en, keyPool_zh):
    database=[]
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    response=requests.get(url,headers=headers)
    json=response.json()
    for one in json['rows'] :
        cell=one['cell']
        # 可转债过滤
        data_dict = {}
        data_dict.fromkeys(keyPool_zh)
        for key,value in cell.items():
            if key in keyPool_en:
                data_dict[keyPool_zh[keyPool_en.index(key)]]=value
           
        database.append(data_dict)
    return pd.DataFrame(database)
def get_cef():
    url="https://www.jisilu.cn/data/cf/cf_list/?___jsl=LST___t=1629637418211"#从Headers的请求URL中获取
    #构造英文pool便于获取所需的value
    keyPool_en=['fund_id','fund_nm','price','discount_rt','annualize_dscnt_rt',
    'style','stock_ratio','left_year','maturity_dt']
    #构造中文pool
    keyPool_zh=['代码','基金名称','现价','折价率','年化折价率','类型',
    '股票占比','剩余年限','到期日期']    
    #if cell['price_tips']=='待上市':
    #continue #筛选掉未上市的股票
    cef = get_pd_data(url, keyPool_en, keyPool_zh)
    cef =cef[cef['剩余年限'].astype('float') < 1.1] 
    cef =cef[cef['剩余年限'].astype('float') > 0.9] 


    cef =cef[cef['折价率'].astype('float') > 9] 
    time = datetime.strftime(datetime.now(),'%Y-%m-%d')
    filename = time + '.xls'
    writer = pd.ExcelWriter(filename)
    cef.to_excel(writer, 'cef')
    for index, row in cef.iterrows():
        xa.fundinfo(row['代码']).get_stock_holdings(2021, 2).to_excel(writer, row['代码'])
    writer.save()
    return cef

def cef_strategy():
    df = get_cef()
    print(df)
    return df


cef = cef_strategy()
print('over')
