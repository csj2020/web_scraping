#!/usr/local/bin/python3.8

import requests
import json, time, random
import logging, sys, os
import pandas as pd
import numpy as np

URL = "https://m.land.naver.com/complex/getComplexArticleList"

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.220 Whale/1.3.51.7 Safari/537.36",
    "Referer": "https://m.land.naver.com/",
}


def get_land(param):
    page = 0
    value_list = [] * 1000
    pd.set_option("display.max_rows", 1000)
    pd.set_option("display.max_columns", 1000)
    pd.set_option("display.width", 1000)
    while True:
        """ Page 증가 설정 """
        page += 1
        param["page"] = page
        time.sleep(random.uniform(3, 7))

        """ 데이터 받아오기 """
        resp = requests.get(URL, params=param, headers=header)
        data = json.loads(resp.text)
        result = data["result"]

        """ 데이터 출력하기 """
        for item in result["list"]:
            value = [
                item["atclNm"],
                item["tradTpNm"],
                item["spc1"],
                item["spc2"],
                item["dtlAddr"],
                item["flrInfo"],
                item["prcInfo"],
                item["rltrNm"],
            ]
            value_list.append(value)

        if result["moreDataYn"] == "N":
            break

    cols = ["아파트명", "거래_타입", "공급_면적", "전용_면적", "호수_정보", "층_정보", "거래_가격", "공인중개사"]
    df = pd.DataFrame(value_list, columns=cols)
    df.sort_values(by="전용_면적", ascending=True)
    df.index = np.arange(1, len(df) + 1)
    html = df.to_html(justify="center")

    with open("apt.html", "a", encoding="utf-8") as file:
        file.writelines('<meta charset="utf-8">\n')
        file.write(html)


# df.index = np.arange(1, len(df) + 1)

apt_list = ["107901", "108832", "107902", "107903", "108834", "107069", "107070"]
# apt_list = {
#     "1단지": "107901",
#     "2단지": "108832",
#     "3단지": "107902",
#     "4단지": "107070",
#     "5단지": "107903",
#     "6단지": "108834",
#     "7단지": "107069",
# }

# 네이버 아파트 코드 확인 법 : view-source:https://m.land.naver.com/complex/info/107901?ptpNo=1
def apt_info(apt_list):
    for list in apt_list:

        param = {
            "hscpNo": list,
            "tradTpCd": "A1",
            "order": "prc",
            "showR0": "N",
        }
        # if param["hscpNo"] == "107901":
        #     print("# 1단지")
        # elif param["hscpNo"] == "108832":
        #     print("# 2단지")
        # elif param["hscpNo"] == "107902":
        #     print("# 3단지")
        # elif param["hscpNo"] == "107070":
        #     print("#4단지")
        # elif param["hscpNo"] == "107903":
        #     print("# 5단지")
        # elif param["hscpNo"] == "108834":
        #     print("# 6단지")
        # elif param["hscpNo"] == "107069":
        #     print("# 7단지")

        get_land(param)
        print()


if __name__ == "__main__":
    filename = "./apt.html"
    if os.path.isfile(filename):
        os.remove(filename)
    apt_info(apt_list)


