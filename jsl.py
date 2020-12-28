import requests
from operator import itemgetter
import pandas as pd


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

def get_jsl_kzz():
    url="https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t=1577251762134"#从Headers的请求URL中获取
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
    
    #if cell['price_tips']=='待上市':
    #continue #筛选掉未上市的股票
    kzz = get_pd_data(url, keyPool_en, keyPool_zh)
        
    kzz=kzz[~kzz['转债名称'].str.contains('EB')]
    kzz=kzz[~kzz['正股名称'].str.contains('ST')]
    return kzz

def get_jsl_found(url):
    #构造英文pool便于获取所需的value
    keyPool_en=['fund_id','fund_nm','price','increase_rt','volume','amount','discount_rt','index_nm']
    #构造中文pool
    keyPool_zh=['代码','基金名称','现价','涨跌幅','成交额','场内份额','溢价率','相关标的']
    found = get_pd_data(url, keyPool_en, keyPool_zh)
    found['基金总值'] = found.apply(lambda x: float(x['现价']) * float(x['场内份额']) / 10000, axis=1)
    return found

def get_jsl_qdii():
    urla="https://www.jisilu.cn/data/qdii/qdii_list/A?___jsl=LST___t=1608033090935&rp=22"
    urlc="https://www.jisilu.cn/data/qdii/qdii_list/C?___jsl=LST___t=1608031747462&rp=22&page=1"
    urle="https://www.jisilu.cn/data/qdii/qdii_list/E?___jsl=LST___t=1608033261594&rp=22&page=1"
    qdii_a = get_jsl_found(urla)
    qdii_c = get_jsl_found(urlc)
    qdii_e = get_jsl_found(urle)
    qdii = qdii_a.append([qdii_c, qdii_e])
    return qdii

def get_jsl_lof():
    url_stock="https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t=1608034413186&rp=25&page=1"
    url_index="https://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___t=1608034597825&rp=25&page=1"
    stock = get_jsl_found(url_stock)
    index = get_jsl_found(url_index)
    lof = stock.append(index)
    return lof

def get_jsl_etf():
    url_etf="https://www.jisilu.cn/data/etf/etf_list/?___jsl=LST___t=1608034730752&rp=25&page=1"
    return get_jsl_found(url_etf)

def kzz_strategy():
    df = get_jsl_kzz()
    #剔除PB小于1
    df = df[df['PB'].astype('float') > 1]
    df = df[df['PB'].astype('float') < 5]
    #剔除成交额小于100万
    df = df[df['成交额'].astype('float') > 100]
    #剔除价格大于115
    df = df[df['现价'].astype('float') < 115]
    #剔除溢价率大于20%
    df = df[(df['溢价率'].str.strip("%").astype('float')/100) < 0.15]
    #剔除剩余年限小于1
    df = df[df['剩余年限'].astype('float') > 1]
    #剔除剩余规模小于5千万
    df = df[df['剩余规模'].astype('float') > 0.5]
    #剔除未到转股期
    df = df[df['转股状态'] != '未到转股期']
    #剔除到期税前收益率小于0
    df = df[(df['到期税后收益'].str.strip("%").astype('float')/100) > 0]
    return df

def qdii_strategy():
    df = get_jsl_qdii()
    df = df[df['基金总值'].astype('float') > 2]
    return df
def lof_strategy():
    df = get_jsl_lof()
    df = df[df['基金总值'].astype('float') > 5]
    return df  
def etf_strategy():
    df = get_jsl_etf()
    df = df[df['基金总值'].astype('float') > 5]
    return df    
kzz = kzz_strategy()
qdii = qdii_strategy()
lof = lof_strategy()
etf = etf_strategy()

writer = pd.ExcelWriter("test.xls")
kzz.to_excel(writer, 'kzz')
qdii.to_excel(writer, 'qdii')
lof.to_excel(writer, 'lof')
etf.to_excel(writer, 'etf')
writer.save()
print('over')
