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


"""
{"result":{"list":[{"repImgUrl":"","atclNo":"2048974752","repImgTpCd":"","vrfcTpCd":"DOC",

"atclNm":"서초포레스타7단지","bildNm":"707동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"87.67","spc2":"59.94","flrInfo":"3/7","atclFetrDesc":" 조용한 친환경 숲세권 단지",
"cfmYmd":"20.07.21","prcInfo":"13억","sameAddrCnt":1,"sameAddrDirectCnt":0,"sameAddrHash":"23A01A1Nd922dc26111edec13811c4517c4eba55ce584e2575f185a16981ad4f1a830c51",
"sameAddrMaxPrc":"13억","sameAddrMinPrc":"13억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"bizmk","cpNm":"매경부동산",
"cpCnt":1,"cpLinkVO":{"cpId":"bizmk","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,
"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},"rltrNm":"내곡좋은터공인중개사사무소","directTradYn":"N",
"direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"707동 303호","dtlAddrYn":"N"},
{"repImgUrl":"","atclNo":"2045930142","repImgTpCd":"","vrfcTpCd":"OWNER",

"atclNm":"서초포레스타7단지","bildNm":"708동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"108.78","spc2":"74.9","flrInfo":"6/7","atclFetrDesc":"청계산입구역, 초역세권, 쾌적한 환경",
"cfmYmd":"20.07.08","tradCmplYmd":"20.07.14","prcInfo":"14억","sameAddrCnt":1,"sameAddrDirectCnt":0,"sameAddrHash":"24A01A1N5986c6be1384187575a11d0f57753839283d8a79a1eacec4f2a08b2d0e0176ca",
"sameAddrMaxPrc":"14억","sameAddrMinPrc":"14억","tradCmplYn":"Y","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R1","cpid":"NEONET","cpNm":"부동산뱅크",
"cpCnt":1,"cpLinkVO":{"cpId":"NEONET","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,
"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},"rltrNm":"정애남공인",
"directTradYn":"N","direction":"","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"708동 604호","dtlAddrYn":"N"},
{"repImgUrl":"","atclNo":"2048932147","repImgTpCd":"","vrfcTpCd":"DOC",

"atclNm":"서초포레스타7단지","bildNm":"707동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"87.67","spc2":"59.94","flrInfo":"고/7","atclFetrDesc":"25형 025794924 청계산역도보3분 앞이트인청계산전망 입주가능","cfmYmd":"20.07.21","prcInfo":"13억","sameAddrCnt":2,
"sameAddrDirectCnt":0,"sameAddrHash":"23A01A1N9d4968ecc9a480edc4661da76300167453221fc65bf35ff8c32b2e6b62f3218f","sameAddrMaxPrc":"13억","sameAddrMinPrc":"13억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"R114","cpNm":"부동산114","cpCnt":1,
"cpLinkVO":{"cpId":"R114","mobileArticleUrl":"https://m.r114.com/?_c=redirect&_m=ArticleFromNbp&UID=","mobileArticleLinkTypeCode":"ALL","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":true,"mobileArticleLinkUseAtCpName":true},
"rltrNm":"포레스타부동산공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"",
"tradeCheckedByOwner":false,"dtlAddr":"707동 601호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2048668930","repImgTpCd":"","vrfcTpCd":"DOC",

"atclNm":"서초포레스타7단지","bildNm":"706동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"122.62","spc2":"84.6","flrInfo":"고/6","atclFetrDesc":"34형 025794924 청계산역도보3분 도심속숲세권 편의시설편리",
"cfmYmd":"20.07.20","prcInfo":"15억","sameAddrCnt":2,"sameAddrDirectCnt":0,"sameAddrHash":"23A01A1N47be29f6b82c33b55ae49caadd41ed7734f5439a1b6f0cf0072769ac96b7c9bf","sameAddrMaxPrc":"15억 5,000","sameAddrMinPrc":"15억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"R114",
"cpNm":"부동산114","cpCnt":2,"cpLinkVO":{"cpId":"R114","mobileArticleUrl":"https://m.r114.com/?_c=redirect&_m=ArticleFromNbp&UID=","mobileArticleLinkTypeCode":"ALL","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":true,"mobileArticleLinkUseAtCpName":true},"rltrNm":"포레스타부동산공인중개사사무소","directTradYn":"N",
"direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"706동 501호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2047338188","repImgTpCd":"","vrfcTpCd":"DOC",

"atclNm":"서초포레스타7단지","bildNm":"708동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"108.78","spc2":"74.9","flrInfo":"6/7","atclFetrDesc":"초역세권, 내부상태 매우좋고 예쁨, 마트,은행 인접","cfmYmd":"20.07.14","prcInfo":"14억","sameAddrCnt":2,"sameAddrDirectCnt":0,
"sameAddrHash":"24A01A1Nb45307dfa6ca56eae9a46d5368e83ffc451203a6c1feee87e49badbaab52c9fb","sameAddrMaxPrc":"14억","sameAddrMinPrc":"14억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],
"atclStatCd":"R0","cpid":"bizmk","cpNm":"매경부동산","cpCnt":2,"cpLinkVO":{"cpId":"bizmk","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,
"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},"rltrNm":"하나공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"708동 603호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2047060670","repImgTpCd":"","vrfcTpCd":"DOC",

"atclNm":"서초포레스타7단지","bildNm":"708동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"108.78","spc2":"74.9","flrInfo":"7/7","atclFetrDesc":"25,남향으로 전망과 채광 최상,중학교 앞단지","cfmYmd":"20.07.13","prcInfo":"14억","sameAddrCnt":1,"sameAddrDirectCnt":0,"sameAddrHash":"24A01A1N886a8b53d32417d4afd1114b2ac3e78e0133e5c9c6c4bfbb34f1e365bf9409fa","sameAddrMaxPrc":"14억","sameAddrMinPrc":"14억","tradCmplYn":"N","tagList":["10년이내","역세권","탑층","방세개"],"atclStatCd":"R0","cpid":"bizmk","cpNm":"매경부동산","cpCnt":1,"cpLinkVO":{"cpId":"bizmk","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},"rltrNm":"내곡좋은터공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"708동 704호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2047120512","repImgTpCd":"","vrfcTpCd":"DOC","atclNm":"서초포레스타7단지","bildNm":"707동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"87.72","spc2":"59.81","flrInfo":"고/7","atclFetrDesc":"초역세권 남향 조망권최상 입주가능","cfmYmd":"20.07.14","prcInfo":"13억","sameAddrCnt":2,"sameAddrDirectCnt":0,"sameAddrHash":"23A01A1N644474603a6825bd72b86f8eb4f9c9b7f7d161dc823eef2ef1b421dc74edc22f","sameAddrMaxPrc":"13억","sameAddrMinPrc":"13억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"JOINS","cpNm":"조인스랜드","cpCnt":2,"cpLinkVO":{"cpId":"JOINS","mobileArticleUrl":"http://m.joinsland.joins.com/maemul/naver/?uid=","mobileArticleLinkTypeCode":"CPNAMEONLY","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":true},"rltrNm":"수부동산공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"707동 504호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2045569387","repImgTpCd":"","vrfcTpCd":"DOC","atclNm":"서초포레스타7단지","bildNm":"708동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"108.78","spc2":"74.9","flrInfo":"5/7","atclFetrDesc":"초역세권,쾌적한 주변환경","cfmYmd":"20.07.07","prcInfo":"14억","sameAddrCnt":3,"sameAddrDirectCnt":0,"sameAddrHash":"24A01A1Nec72cdd3ae4fbab11bb035dd1e731e1a07e838014f1b119f6fe2b57e00e8fb24","sameAddrMaxPrc":"14억","sameAddrMinPrc":"14억",
"tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"bizmk","cpNm":"매경부동산",
"cpCnt":2,"cpLinkVO":{"cpId":"bizmk","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},
"rltrNm":"청계산역공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"708동 505호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2046986245","repImgTpCd":"","vrfcTpCd":"DOC","atclNm":"서초포레스타7단지","bildNm":"706동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"122.62","spc2":"84.6","flrInfo":"중/6","atclFetrDesc":"34형 025794924 청계산역3분거리 숲세권 선호구조 밝은집","cfmYmd":"20.07.13","prcInfo":"15억","sameAddrCnt":1,"sameAddrDirectCnt":0,"sameAddrHash":"23A01A1N32ce61c2e4ce0f40867517f91562309f56eba907d790f5fee906376bfc8a5c90","sameAddrMaxPrc":"15억","sameAddrMinPrc":"15억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"R114","cpNm":"부동산114","cpCnt":1,"cpLinkVO":{"cpId":"R114","mobileArticleUrl":"https://m.r114.com/?_c=redirect&_m=ArticleFromNbp&UID=","mobileArticleLinkTypeCode":"ALL","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":true,"mobileArticleLinkUseAtCpName":true},"rltrNm":"포레스타부동산공인중개사사무소","directTradYn":"N","direction":"남서향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"706동 301호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2045308447","repImgTpCd":"","vrfcTpCd":"DOC","atclNm":"서초포레스타7단지","bildNm":"708동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"108.78","spc2":"74.9","flrInfo":"5/7","cfmYmd":"20.07.06","prcInfo":"14억","sameAddrCnt":1,"sameAddrDirectCnt":0,"sameAddrHash":"24A01A1N30ee1491a43009e28438c7660a8c290783cfb9c7cea8fcb836eaffb62db6d6b7","sameAddrMaxPrc":"14억","sameAddrMinPrc":"14억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"R114","cpNm":"부동산114","cpCnt":1,"cpLinkVO":{"cpId":"R114","mobileArticleUrl":"https://m.r114.com/?_c=redirect&_m=ArticleFromNbp&UID=","mobileArticleLinkTypeCode":"ALL","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":true,"mobileArticleLinkUseAtCpName":true},"rltrNm":"가온공인중개사사무소","directTradYn":"N","direction":"","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"708동 504호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2044953012","repImgTpCd":"","vrfcTpCd":"DOC","atclNm":"서초포레스타7단지","bildNm":"708동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"108.78","spc2":"74.9","flrInfo":"5/7","atclFetrDesc":"30 남향 신분당선초역세권 청계산숲세권 조용 깨끗","cfmYmd":"20.07.04","prcInfo":"14억","sameAddrCnt":1,"sameAddrDirectCnt":0,"sameAddrHash":"24A01A1Nb33a4744a92835dd62e9db378d8543e6a7b858f0145da72a661b94ced7e39f7e","sameAddrMaxPrc":"14억","sameAddrMinPrc":"14억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"hkdotcom","cpNm":"한경부동산","cpCnt":1,"cpLinkVO":{"cpId":"hkdotcom","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},"rltrNm":"서초공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"708동 503호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2045825858","repImgTpCd":"","vrfcTpCd":"TEL","atclNm":"서초포레스타7단지","bildNm":"706동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"123.42","spc2":"84.79","flrInfo":"고/6","atclFetrDesc":"37 2분초역세권 조용 쾌적 숲세권 입주가","cfmYmd":"20.07.08","prcInfo":"15억","sameAddrCnt":2,"sameAddrDirectCnt":0,"sameAddrHash":"23A01A1Nfe29677b41292ecb2c19befd127c705ab91addd8966249f7350252d32aecc35a","sameAddrMaxPrc":"15억 5,000","sameAddrMinPrc":"15억","tradCmplYn":"N","tagList":["10년이내","역세권","방세개","화장실두개"],"atclStatCd":"R0","cpid":"bizmk","cpNm":"매경부동산","cpCnt":2,"cpLinkVO":{"cpId":"bizmk","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},"rltrNm":"성심공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"706동 502호","dtlAddrYn":"N"},{"repImgUrl":"","atclNo":"2041806379","repImgTpCd":"","vrfcTpCd":"DOC","atclNm":"서초포레스타7단지","bildNm":"708동","tradTpCd":"A1","tradTpNm":"매매","rletTpCd":"A01","rletTpNm":"아파트","spc1":"108.78","spc2":"74.9","flrInfo":"7/7","atclFetrDesc":"남향 청계산역도보3분이내 숲세권 깨끗 편의시설","cfmYmd":"20.06.25","prcInfo":"14억","sameAddrCnt":1,"sameAddrDirectCnt":0,"sameAddrHash":"24A01A1N721d509affb727e415074d28ac1f8ae301bdd9458aaccb7bf82ce51c19bd6566","sameAddrMaxPrc":"14억","sameAddrMinPrc":"14억","tradCmplYn":"N","tagList":["10년이내","역세권","탑층","방세개"],"atclStatCd":"R0","cpid":"hkdotcom","cpNm":"한경부동산","cpCnt":1,"cpLinkVO":{"cpId":"hkdotcom","mobileArticleLinkTypeCode":"NONE","mobileBmsInspectPassYn":"Y","pcArticleLinkUseAtArticleTitle":false,"pcArticleLinkUseAtCpName":false,"mobileArticleLinkUseAtArticleTitle":false,"mobileArticleLinkUseAtCpName":false},"rltrNm":"서초공인중개사사무소","directTradYn":"N","direction":"남향","tradePriceHan":"","tradeRentPrice":0,"tradePriceInfo":"","tradeCheckedByOwner":false,"dtlAddr":"708동 705호","dtlAddrYn":"N"}],"totAtclCnt":13,"moreDataYn":"N"}}


"""

