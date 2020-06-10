#!/usr/local/bin/python3.8

import time, re, sys, datetime, os
import urllib.request, json, mariadb, pytz
from pandas import DataFrame
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler 

def api_get_date():
    standard_time = [ 2, 5, 8, 11, 14, 17, 20, 23 ]  # api response time. 1일 8회의 기상정보를 제공한다. 각 시간의 10분에 API 제공된다.
    time = datetime.datetime.now(tz=pytz.timezone("Asia/Seoul")).strftime("%Y%m%d%H")
    time_now = time[8:]  # 현재 시간을 저장
    check_time = int(time_now) - 1
    day_calibrate = 0

    while not check_time in standard_time:
        check_time = check_time - 1
        if check_time < 2:  # 지금 체크를 돌린 시간이 2시도 안된다면
            day_calibrate = 1  # 날짜를 하루 되돌리기 위한 변수다.
            check_time = 23  # 되돌려진 하루 전에서 가장 큰 기상정보 제공 시간은 23시이다
    date_now = time[:8]  # ex) 2020-05-25
    check_date = int(date_now) - day_calibrate  # day_calibrate 에 값이 있다면 하루 되돌려진다

    if len(str(check_time)) == 1:
        check_time = "0" + str(check_time) + "00"
    elif len(str(check_time)) == 2:
        check_time = str(check_time) + "00"

    return (str(check_date), (str(check_time)))


def get_weather_data(x, y):
    api_date, api_time = api_get_date()
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?"
    key = (
        "serviceKey="
        + "%2FKmMCVQsc00Z1K0UN%2FRo5XbVIroiF%2Fb2bZ47XJ8LoLCdv6LOnHETW6aY0aNS5wJL9vlw9XNgCokdH11cVx%2FINA%3D%3D"
    )
    numofrows = "&numOfRows=" + "10"
    pageno = "&pageNo=" + "1"
    base_date = "&base_date=" + api_date
    base_time = "&base_time=" + api_time
    
    if x == 0 and y == 0:
        nx = "&nx=" + "61"
        ny = "&ny=" + "126"
    else: 
        nx = "&nx=" + x
        ny = "&ny=" + y
    print(nx, ny)
    datatype = "&dataType=" + "json"
    api_url = (
        url + key + numofrows + pageno + base_date + base_time + nx + ny + datatype
    )
    data = (
        urllib.request.urlopen(api_url).read().decode("utf8")
    )  # 주어진 url 의 내용을 utf-8로 디코드하며 읽는 메서드이다.
    data_json = json.loads(data)
    parsed_json = data_json["response"]["body"]["items"][
        "item"
    ]  # response{ 'header': {...}, 'body': {..., 'items': {'item': {...}}}} 를 찾아가는 경로이다.
    target_date = parsed_json[0]["fcstDate"]
    target_time = parsed_json[0]["fcstTime"]
    passing_data = {}
    #    date_calibrate = target_date    # date of TMX, TMN
    #    if target_time > '1300':
    #        date_calibrate = str(int(target_date) + 1)

    for one_parsed in parsed_json:
        # one_parsed 의 출력 형태 : {'baseDate': '20200524', 'baseTime': '2300', 'category': 'POP', 'fcstDate': '20200525', 'fcstTime': '0300', 'fcstValue': '20', 'nx': 55, 'ny': 127}
        if (
            one_parsed["fcstDate"] == target_date
            and one_parsed["fcstTime"] == target_time
        ):
            passing_data[one_parsed["category"]] = one_parsed["fcstValue"]
            # passing_data 의 데이터가 누적되는 과정
            # {'POP': '20'}
            # {'POP': '20', 'PTY': '0'}
            # {'POP': '20', 'PTY': '0', 'REH': '95'}
            # {'POP': '20', 'PTY': '0', 'REH': '95', 'SKY': '3'}
            # {'POP': '20', 'PTY': '0', 'REH': '95', 'SKY': '3', 'T3H': '14'}
            # {'POP': '20', 'PTY': '0', 'REH': '95', 'SKY': '3', 'T3H': '14', 'UUU': '0.4'}
            # {'POP': '20', 'PTY': '0', 'REH': '95', 'SKY': '3', 'T3H': '14', 'UUU': '0.4', 'VEC': '214'}
            # {'POP': '20', 'PTY': '0', 'REH': '95', 'SKY': '3', 'T3H': '14', 'UUU': '0.4', 'VEC': '214', 'VVV': '0.6'}
            # {'POP': '20', 'PTY': '0', 'REH': '95', 'SKY': '3', 'T3H': '14', 'UUU': '0.4', 'VEC': '214', 'VVV': '0.6', 'WSD': '0.7'}

    #   if one_parsed['fcstDate'] == date_calibrate and (one_parsed['category'] == 'TMX' or one_parsed['category'] == 'TMN'):   # TMX, TMN 이 안쌓이고 있다. 바뀐 점이 있는지 명세표 확인 필요
    #        passing_data[one_parsed['category']] = one_parsed['fcstValue']
    return passing_data


def weather_data(result):
    # 날씨 정보 해석을 위한 비교 데이터
    data = """      
PTY 0 날씨정보 없음
PTY 1 비
PTY 2 비 또는 눈
PTY 3 눈
PTY 4 소나기
SKY 1 맑음
SKY 3 구름 많음
SKY 4 흐림  """
    msg = []
    ma = msg.append
    ma("오늘은 " + time.ctime()[:11] + "입니다\n")
    for x, y in result.items():
        if x in ["PTY", "SKY"]:
            code = x
            code_num = y
            word = f"^{code}\s{code_num}\s(.+)"
            match = re.compile(f"{word}", re.MULTILINE)
            if x == "PTY":
                msg.append("강수 형태는 " + match.search(data).group(1) + "입니다\n")
            if x == "SKY":
                msg.append("날씨는 " + match.search(data).group(1) + "이며 ")
        # if x in ['POP', 'REH']:
        if x == "POP":
            msg.append("강수 확률은 " + result[x] + "%입니다")
        if x == "REH":
            msg.append("습도는 " + result[x] + "%이고 ")

    short = DataFrame(msg).values  # 0, 4, 2, 3, 1 순서로 실행하면 날씨 읽어보기에 좋다.
    return short[0] + short[4] + short[2] + short[3] + short[1]


def db_insert(result):
    config = {"host": "localhost", "user": "jh", "password": "", "database": "scraping"}
    try:
        conn = mariadb.connect(**config)
    except mariadb.Error as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO weather VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            time.strftime("%m/%d %H:%M"),
            result["POP"],
            result["PTY"],
            result["REH"],
            result["SKY"],
            result["T3H"],
            result["UUU"],
            result["VEC"],
            result["VVV"],
        ),
    )

    cur.execute("SELECT * FROM weather")
    conn.close()
    ## Database Insert
    # brew install mariadb
    # DB와 Table 생성
    # cur.execute("CREATE DATABASE scraping")
    # cur.execute("CREATE TABLE weather(DATE_TIME VARCHAR(255), POP VARCHAR(255), PTY VARCHAR(255), REH VARCHAR(255), SKY VARCHAR(255),
    #                                                           T3H VARCHAR(255), UUU VARCHAR(255), VEC VARCHAR(255), VVV VARCHAR(255)")

    # +-----------+--------------+------+-----+---------+-------+
    # | Field     | Type         | Null | Key | Default | Extra |
    # +-----------+--------------+------+-----+---------+-------+
    # | DATE_TIME | varchar(255) | YES  |     | NULL    |       |
    # | POP       | varchar(255) | YES  |     | NULL    |       |
    # | PTY       | varchar(255) | YES  |     | NULL    |       |
    # | REH       | varchar(255) | YES  |     | NULL    |       |
    # | SKY       | varchar(255) | YES  |     | NULL    |       |
    # | T3H       | varchar(255) | YES  |     | NULL    |       |
    # | UUU       | varchar(255) | YES  |     | NULL    |       |
    # | VEC       | varchar(255) | YES  |     | NULL    |       |
    # | VVV       | varchar(255) | YES  |     | NULL    |       |
    # +-----------+--------------+------+-----+---------+-------+
    # +-------------+------+------+------+------+------+------+------+------+------+
    # | DATE_TIME   | POP  | PTY  | REH  | SKY  | T3H  | UUU  | VEC  | VVV  | WSD(삭제)|
    # +-------------+------+------+------+------+------+------+------+------+------+
    # | 05/27 01:05 | 0    | 0    | 95   | 1    | 14   | 0    | 135  | 0.1  |      |
    # +-------------+------+------+------+------+------+------+------+------+------+



def get_message(bot, update) :
    #update.message.reply_text(update.message.text)
    res = update.message.text
    
    if res == "1":
        update.message.reply_text(res + " 을(를) 입력 받았습니다")
        '''
        Weather API
        x, y 좌표값을 인자로 주어 실행하면 return 타입이 numpy로 변경된다. [0]인자로 데이터를 가져오는 이유.
        '''
        x, y = 0, 0
        result    = get_weather_data(x, y)
        newmsg    = weather_data(result)[0]    
        '''
        임의 지역의 데이터를 DB에 넣으면 의미없는 데이터라 제외함. 
        통계 데이터를 고려한다면 동네 구분도 되게끔 컬럼 추가하는 게 필요할 듯함.
        db_insert(result)
        '''
        for txt in newmsg.split('\r'):
            jhbot.sendMessage(chat_id = cid, text = txt)

    elif res == "2":
        update.message.reply_text(res + " 을(를) 입력 받았습니다")     
        jhbot.sendMessage(chat_id = cid, text = '동네명을 입력하세요. (10초)') 
        update.message.text          # if문 안에서는 update.message.text 가 갱신되지 않고 있다.
        time.sleep(5)                

        
        '''
        while True:
            """
            동네 명을 입력 받아 구를 확인한다.
            구를 확인하면 구와 동네명을 입력 받는다.
            """
            jhbot.sendMessage(chat_id = cid, text = '동네명을 입력하세요. (10초)')
            time.sleep(10)
            
            response = update.message.text
            update.message.reply_text(response + " 을(를) 입력 받았습니다")
            find_addr(response)
            if len(response) == 1 or len(response) == 2 :
                break
        '''
    elif res == "3":
        jhbot.sendMessage(chat_id = cid, text = '챗봇을 종료합니다')
        os._exit(1)
    
    update.message.text    # 여기에서는 동네명을 받아온다. 
#    print('실행전: ', update)
    if res != "1" and res != "2":
        res = update.message.text
        update.message.reply_text(res + " 을(를) 입력 받았습니다")
        res = res.split()
        if len(res) == 1:
            jhbot.sendMessage(chat_id = cid, text = find_addr(str(res[0])))
            print(str(res[0]))
        elif len(res) == 2:
            jhbot.sendMessage(chat_id = cid, text = find_addr(str(res[0]), str(res[1])))
            print(str(res[0], res[1]))
           # for txt in res:
           #     print('res[txt]: res[{0}], type은 {1}'.format(txt, type(txt)))
           #     jhbot.sendMessage(chat_id = cid, text = find_addr(txt))
        else: print('정확하게 입력하세요')

def find_addr(*address1):
    if len(address1) == 1:                  # length가 1이면 동주소만 입력되는 최초 검색 처리 부분이다.
        p = re.compile(rf'(\w+)\s+(\w+)\s+({address1[0]})+\s+(\w+)\s+(\w+)\s+')
        with open('data.txt', 'r') as f:
            jhbot.sendMessage(chat_id = cid, text = f'{address1[0]} 을(를) 검색합니다')
            jhbot.sendMessage(chat_id = cid, text = 'USAGE: 아래 주소 중 정확한 주소를 입력하세요. ex) 강남구 압구정동')
            for txt in f.readlines():
                if p.search(txt):
                    jhbot.sendMessage(chat_id = cid, text = txt)

    elif len(address1) == 2:
        p = re.compile(rf'(\w+)\s+({address1[0]})\s+({address1[1]})\s+(\d+)\s+(\d+)\s+')
        with open('data.txt', 'r') as f:
            for txt in f.readlines():
                if p.search(txt):   
                    print(my_vil := p.search(txt).group(2,3,4,5))
                    region = my_vil[0] + my_vil[1]
                    result = get_weather_data(my_vil[2], my_vil[3])
                    newmsg = weather_data(result)[0]
                    jhbot.sendMessage(chat_id = cid, text = my_vil[0] + '' + my_vil[1] + ' 날씨입니다')
                    for txt in newmsg.split('\r'):
                        jhbot.sendMessage(chat_id = cid, text = txt)


    '''
     update:  
     {'message_id': 1041, 
     'date': 1591353234, 
     'chat': {'id': 798670742, 'type': 'private', 'first_name': 'jinho'}, 
     'text': 'sdjflsdkfjsdlkfjsd', 
     'entities': [], 
     'caption_entities': [], 
     'photo': [], 
     'new_chat_members': [], 
     'new_chat_photo': [], 
     'delete_chat_photo': False, 
     'group_chat_created': False, 
     'supergroup_chat_created': False, 
     'channel_chat_created': False, 
     'from': {'id': 798670742, 'first_name': 'jinho', 'is_bot': False, 'language_code': 'en'}}
    '''


def func_stop(bot, update):
    jhbot.sendMessage(chat_id = cid, text = '챗봇 사용을 종료합니다')
    os._exit(1)

def start_info():
    infomsg = """
        챗봇 사용을 시작합니다

        사용법 : 
                입력: 1  
                서울특별시 강남구 청담동 날씨가 출력됩니다.
                
                입력: 2
                지역의 날씨가 출력됩니다.                 
                구와 동네명을 입력하세요. 정확한 주소를 모를 경우 동네명을 입력하세요.

                입력: 3
                프로그램을 종료합니다. """

    for txt in infomsg.split('\r'):
        jhbot.sendMessage(chat_id = cid, text = txt)

# def bot_weather(bot, update):
#     for wea in msg:
#         jhbot.sendMessage(chat_id = cid, text = wea)


def main():

    
    # ChatBot Function execute
    # 메시지 보내는 과정 : telegram.Bot(토큰키).sendMessage(chat_id = 챗룸ID, text = 발송내용)
    
    # 안내 메시지 발송
    start_info()

    # /stop 명령 처리기
    #command_handlerStop = CommandHandler('stop', func_stop)
    #updater.dispatcher.add_handler(command_handlerStop)
    
    # /weather 명령 처리기
    #command_handlerWeather = CommandHandler('weather', bot_weather)
    #updater.dispatcher.add_handler(command_handlerWeather)
    
    # 주소 값을 받아오는 챗봇 기능
    message_handler = MessageHandler(Filters.text, get_message) # 실제 메시지를 저장하는 역할하고 있다. 
    updater.dispatcher.add_handler(message_handler)

    # 텔레그램과 연결 유지
    updater.start_polling(timeout=3, clean=True)
    updater.idle()



if __name__ == "__main__":

    # ChatBot
    my_token = '1215765058:AAG68ELcpZ3nYsWOcN88r6m8N4svbb6_lmo'
    #updater  = Updater(my_token, use_context=True)
    updater  = Updater(my_token)
    jhbot    = telegram.Bot(my_token)
    cid      = 798670742
    
    main()

# TIP : 같은 폴더에 오류가 있는 파이썬 파일이 있을 경우 같이 오류가 발생한다.
#       import 안해도 라이브러리 파일로 인식해 오류 나는 듯하다



### 해결책은 여기에서 . 찍고 메서드 확인해보자. 그게 가장 확실해보인다. ### 

# https://www.codementor.io/@garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay 참고중
