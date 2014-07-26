import requests
from lxml import etree
import datetime
import pandas

HISTORICAL='http://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml'
DAILY='http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'

def get_and_parse(data_url):
    result = requests.get(data_url)
    if result.status_code == requests.codes.ok:
        return parse_and_load(result.content)
        
def parse_and_load(content):
    data = []
    doc = etree.XML(content)
    nodes = doc.iterchildren()
    subject = nodes.next()
    sender = nodes.next()
    parent_cube = nodes.next()
    times,currencies = get_index_and_cols(parent_cube)
    df = pandas.DataFrame(index=times,columns=currencies)
    load_dataframe(df,parent_cube)
    return df
    

def load_dataframe(df,node):
    for daily_cube in node.iterchildren():
        time = daily_cube.attrib['time']
        for currency_cube in daily_cube.iterchildren():
            currency = currency_cube.attrib['currency']
            rate = currency_cube.attrib['rate']
            df.ix[time,currency] = rate

def get_index_and_cols(node):
    times = []
    currencies = []
    for daily_cube in node.iterchildren():
        time = daily_cube.attrib['time']
        times.append(time)
        for currency_cube in daily_cube.iterchildren():
            currency = currency_cube.attrib['currency']
            if currency not in currencies:
                currencies.append(currency)
    return (times,currencies)
                    
def get_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

def get_historical_data_df():
    return get_and_parse(HISTORICAL)

def get_daily_data_df():
    return get_and_parse(DAILY)