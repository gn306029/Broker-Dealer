import requests as req
import re
import time

from bs4 import BeautifulSoup
from itertools import groupby
from datetime import datetime

def get_curr_date():
    import platform

    # 去除月份前導 0 , 不同作業系統的做法不一樣
    if platform.system() == "Windows":
        return datetime.now().strftime("%Y-%#m-%d")
    else:
        return datetime.now().strftime("%Y-%-m-%d")

def format_amount(value):
    return int(value.replace(",", ""))

def get_data(start, end, broker_id, seller_id):

    data = {}

    res = req.get(f"http://jsjustweb.jihsun.com.tw/z/zg/zgb/zgb0.djhtm?a={broker_id}&b={seller_id}&e={start}&f={end}")

    soup = BeautifulSoup(res.text, 'html.parser')

    table = soup.find(id="oMainTable")
    content_tr = table.find_all("tr")

    for tr in content_tr:
        script = tr.find("script")

        stock_id = None
        stock_name = None

        buying_amount = 0
        selling_amount = 0
        diff_amount = 0

        if script:
            comment = re.search(r"(?<=\().+?(?=\))", script.text)
            if comment:
                stock_info = comment.group(0).split(",")

                if len(stock_info) == 2:
                    stock_id, stock_name = stock_info
        
        if not stock_id and not stock_name: continue
        
        amount_td = tr.find_all("td", {"class": "t3n1"})

        buying_amount += format_amount(amount_td[0].text)
        selling_amount += format_amount(amount_td[1].text)
        diff_amount += format_amount(amount_td[2].text)

        if diff_amount < 3000: continue

        data[stock_id] = {
            "stock_name": stock_name,
            "buying_amount": buying_amount,
            "selling_amount": selling_amount,
            "diff_amount": diff_amount
        }

    return data

def analysis_data(result, filters={}):
    # 比對資料
    compare_res = []

    # 每個券商都要進行比對
    # 把資料整理成 [Group_id, Stock_id, ...]
    # 再用 GroupBy 整合
    
    new_result = []

    for broker_id, stock_info in result.items():
        for stock_id, trade_info in stock_info.items():
            new_result.append([
                broker_id,
                stock_id,
                trade_info
            ])
    
    # 按照股票代號排序
    new_result = sorted(new_result, key=lambda r: r[1])
    group_data = groupby(new_result, key=lambda r: r[1])

    for stock_id, group_info in group_data:
        d = list(group_info)
        
        if len(d) > 1:
            compare_res.append([stock_id, d])
    
    return compare_res

def run(args={}):
    target_broker = args.get("target_broker", [])
    start_date = args.get("start_date", get_curr_date())
    end_date = args.get("end_date", get_curr_date())

    result = {}

    for broker_id, seller_id in target_broker:
        res = get_data(start_date, end_date, broker_id, seller_id)

        result[seller_id] = res

        time.sleep(1)
    
    final_data = analysis_data(result)
    final_data = sorted(final_data, key=lambda r: len(r[1]), reverse=True)

    if args.get("print"):
        print(final_data)

    return final_data

if __name__ == "__main__":
    import json

    data = run({
        "target_broker": [
            ("9200", "9216"), # 凱基信義
            ("9A00", "0039004100390052"), # 永豐金信義
            ("8560", "8564"), # 新光台南
            ("7790", "003700370039005a"), # 國票安和
        ],
        "start_date": "2022-5-10",
        "end_date": "2022-5-13",
        "print": True
    })

    print(json.dumps(data))