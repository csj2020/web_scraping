#!/usr/local/bin/python3.8

import time, re, sys, datetime
import urllib.request, pytz, json, telegram, mariadb
from pandas import DataFrame


def api_get_date():
    standard_time  = [2, 5, 8, 11, 14, 17, 20, 23]                                              # api response time. 1일 8회의 기상정보를 제공한다. 각 시간의 10분에 API 제공된다.
    time           = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul')).strftime('%Y%m%d%H')
    time_now       = time[8:]                                                                   # 현재 시간을 저장
    check_time     = int(time_now) - 1
    day_calibrate  = 0
    
    while not check_time in standard_time:
        check_time = check_time - 1
        if check_time < 2:                                                                     # 지금 체크를 돌린 시간이 2시도 안된다면
            day_calibrate = 1                                                                  # 날짜를 하루 되돌리기 위한 변수다. 
            check_time    = 23                                                                 # 되돌려진 하루 전에서 가장 큰 기상정보 제공 시간은 23시이다
    date_now = time[:8]                                                                        # ex) 2020-05-25
    check_date = int(date_now) - day_calibrate                                                 # day_calibrate 에 값이 있다면 하루 되돌려진다
    
    if len(str(check_time))   == 1: check_time = '0' + str(check_time) + '00'
    elif len(str(check_time)) == 2: check_time = str(check_time) + '00'

    return (str(check_date), (str(check_time)))

def get_weather_data():
    api_date, api_time = api_get_date()
    url            = "http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst?"
    key            = "serviceKey=" + "%2FKmMCVQsc00Z1K0UN%2FRo5XbVIroiF%2Fb2bZ47XJ8LoLCdv6LOnHETW6aY0aNS5wJL9vlw9XNgCokdH11cVx%2FINA%3D%3D"
    numofrows      = "&numOfRows=" + "10"
    pageno         = "&pageNo=" + "1"
    base_date      = "&base_date=" + api_date
    base_time      = "&base_time=" + api_time
    nx             = "&nx=" + "62"
    ny             = "&ny=" + "123"
    datatype       = "&dataType=" + "json"
    api_url        = url + key + numofrows + pageno + base_date + base_time + nx + ny + datatype
    data           = urllib.request.urlopen(api_url).read().decode('utf8')            # 주어진 url 의 내용을 utf-8로 디코드하며 읽는 메서드이다.
    data_json      = json.loads(data)
    parsed_json    = data_json['response']['body']['items']['item']                   # response{ 'header': {...}, 'body': {..., 'items': {'item': {...}}}} 를 찾아가는 경로이다.
    target_date    = parsed_json[0]['fcstDate']     
    target_time    = parsed_json[0]['fcstTime']
    passing_data   = {}    
#    date_calibrate = target_date    # date of TMX, TMN
#    if target_time > '1300':
#        date_calibrate = str(int(target_date) + 1)
    
    for one_parsed in parsed_json:
        # one_parsed 의 출력 형태 : {'baseDate': '20200524', 'baseTime': '2300', 'category': 'POP', 'fcstDate': '20200525', 'fcstTime': '0300', 'fcstValue': '20', 'nx': 55, 'ny': 127}
        if one_parsed['fcstDate'] == target_date and one_parsed['fcstTime'] == target_time:
            passing_data[one_parsed['category']] = one_parsed['fcstValue']
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
    ma  = msg.append
    ma('오늘은 ' + time.ctime()[:11] + '입니다\n')
    for x, y in result.items():
        if x in ['PTY', 'SKY']:
            code     = x
            code_num = y
            word     = f'^{code}\s{code_num}\s(.+)'
            match    = re.compile(f'{word}', re.MULTILINE)
            if x == 'PTY': msg.append('강수 형태는 ' + match.search(data).group(1) + '입니다\n')
            if x == 'SKY': msg.append('날씨는 '     + match.search(data).group(1) + '이며 ')
        #if x in ['POP', 'REH']:
        if x == 'POP': msg.append('강수 확률은 ' + result[x] + '%입니다')
        if x == 'REH': msg.append('습도는 '     + result[x] + '%이고 ')   
        
    short = DataFrame(msg).values    # 0, 4, 2, 3, 1 순서로 실행하면 날씨 읽어보기에 좋다.
    return (short[0] + short[4] + short[2] + short[3] + short[1])

def db_insert(result):
    config = {
    'host': 'localhost',
    'user': 'jh',
    'password': '',
    'database': 'scraping'
    }
    try:
        conn = mariadb.connect(**config)
    except mariadb.Error as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    cur = conn.cursor()
    cur.execute("INSERT INTO weather VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (time.strftime("%m/%d %H:%M"), result['POP'], result['PTY'], result['REH'], result['SKY'], result['T3H'], result['UUU'], result['VEC'], result['VVV'],))

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


def telegram_send(msg):
    # Telegram 
    telgm_token = '1100317510:AAHj4lKEBTELIR-vnrN62Mnk4YvCHH_3ql4'
    bot = telegram.Bot(token=telgm_token)
    updates = bot.getUpdates()                 # 무언가를 주기적으로 타이핑해주어야 챗봇이 끊기지 않고 있다. 업데이트 내역을 받아온다.
    telid = []
    for u in updates:               
        telid = u.message['chat']['id']
    bot.sendMessage(chat_id=telid, text=msg[0])


def main():
    result = get_weather_data()
    msg = weather_data(result)
    db_insert(result)
    telegram_send(msg)                        # 출력 형태 : {'POP': '20', 'PTY': '0', ...... , 'WSD': '0.7'}

if __name__ == '__main__':
    main()
