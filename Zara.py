from Parser.Utils import *
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import os
import time
import datetime

URL_ZARA_HOME = "https://www.zara.com/uk/"


def get_categories() -> []:
    raw_html = simple_get(URL_ZARA_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')

    results = html.findAll(name="li", attrs={"data-layout": "products-category-view"})
    output = []
    for result in results:
        try:
            output.append(result.find("a")["href"])
            # print(result)
        except:
            try:
                output.append(result.find("a")["data-href"])
            except:
                print("error: {}".format(result))
    return output


def get_inventory(url: str):
    time.sleep(1)
    print(url)
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')

    pattern = re.compile(r"window.zara.dataLayer\s+=\s+(\{.*?\});window.zara.viewPayload = window.zara.dataLayer")
    scripts = html.find_all("script", text=pattern)
    try:
        for script in scripts:
            data = pattern.search(script.text).group(1)
            data = json.loads(data)

            products = []
            i = 0
            for node in data["productGroups"][0]["products"]:
                try:
                    if "price" in node:
                        products.append({"shop": "Zara",
                                         "id": node["id"],
                                         "reference": node["detail"]["reference"],
                                         "name": node["name"],
                                         "price": node["price"],
                                         "taxo1": node["sectionName"],
                                         "taxo2": node["familyName"],
                                         "taxo3": node["subfamilyName"]})
                    else:
                        products.append({"shop": "Zara",
                                         "id": node["id"],
                                         "reference": node["detail"]["reference"],
                                         "name": node["bundleProductSummaries"][0]["name"],
                                         "price": node["bundleProductSummaries"][0]["price"],
                                         "taxo1": node["sectionName"],
                                         "taxo2": node["familyName"],
                                         "taxo3": node["subfamilyName"]})
                except Exception as err:
                    i += 1
                    print("{}/{} : {}".format(i, len(data["productGroups"][0]["products"]), err))

    except Exception:
        print("URL EXCEPTION: {}".format(url))
        return None
    return (pd.DataFrame(products))


def parse_zara():
    # get url to analyse
    list_url = get_categories()
    # get inventory
    df_list = [get_inventory(x) for x in list_url]
    df = pd.concat(df_list)
    now = datetime.datetime.now()
    df.to_csv(os.path.join(DIRECTORY_TMP, "zara_{}-{}-{}.csv".format(now.year, now.month, now.day)))


parse_zara()
