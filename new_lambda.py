import json, os, re, boto3, random, time
import requests, pymysql
from collections import defaultdict

# 정상 동작함. (완료)


def lambda_handler(event, context):
    # Enviroment settings
    webhook_url   = os.environ['webhook_url']
    channel       = os.environ['channel']
    slack_config(event, context, webhook_url, channel)


def slack_config(event, context, webhook_url, channel):
    # Slack Variables
    #ids           = event['id']
    #region        = event['region']
    status        = event['detail']['state']
    id            = event['detail']['instance-id']
    ec2_vars      = []
    
    # Boto Instance Variables
    '''
    vpcid         = instance.vpc_id
    ins_type      = instance.instance_type
    '''
    ec2           = boto3.resource('ec2', region_name = 'ap-northeast-2')
    instance      = ec2.Instance(id)
    imgid         = instance.image_id
    ins_pri_ip    = instance.private_ip_address
    tag           = [ tag['Value'] for tag in instance.tags if tag['Key'] == 'Name' ][0]
    
    '''
    terminated 상태에서는 IP Address 가 반환된 상태이기에 결과값이 없다    
    #ec3 = boto3.resource('ec2')
    #vpc_address = ec3.VpcAddress('allocation_id')
    '''

    # Boto Image Variables
    image          = ec2.Image(imgid)
    platform       = image.platform_details.split('/')[0]
    imgver         = image.name
    tmp_ver        = re.search(r'(\w+)-(\w+)-(\w+)', imgver).group(1,2)
    ver            = tmp_ver[0] + tmp_ver[1]
    '''
    출력 결과 
    1. 플랫폼
    2. 인스턴스 상태
    3. 호스트네임
    4. 인스턴스 IP 
    5. 인스턴스 ID
    6. 운영체제 버전
    '''
    ec2_vars.append('{0} {1} {2} {3} {4} {5}'.format(platform, status, tag, ins_pri_ip, id, ver))

    # send a message to slack
    slack_send(webhook_url, ec2_vars)
    
    # Insert Data
    insert_db(platform, status, tag, ins_pri_ip, id, ver, webhook_url)

def slack_send(webhook_url, ec2_vars):
    sending        = requests.post
    msg            = ec2_vars
    for txt in msg:
        sending(
            webhook_url,
            data    = json.dumps({"text": txt}),
            headers = {'Content-Type': 'application/json'}
            )

def insert_db(platform, status, tag, ins_pri_ip, id, ver, webhook_url):
    os_type         = '1' if platform.lower() == 'windows' else '4'
    req_random      = ''.join([ str(random.randint(0,9)) for n in range(0,3)])
    req_id          = time.strftime('%H%M%S', time.localtime(time.time())) + req_random
    db              = pymysql.connect(
                                 host='10.180.104.14', 
                                 port=3306, 
                                 user='', 
                                 passwd=os.environ['db_passwd'], 
                                 db='', 
                                 charset='utf8')    
    sql             = f"select DEV_HOSTNAME from REQUEST_DEVICE where DEV_HOSTNAME = '{id}'"
    main_sql        = '''insert into REQUEST_MAIN(REQ_ID, REQ_TYPE, R_TIME) values (%s, %s, %s)'''  
    device_sql      = '''insert into REQUEST_DEVICE(REQ_ID, DEV_NAME, DEV_IP, DEV_HOSTNAME, OS_TYPE, OS_VERSION)
                        values (%s, %s, %s, %s, %s, %s)'''  

    try:
        with db.cursor() as cursor:
            if int(cursor.execute(sql))  == 0 or int(cursor.execute(sql)) == '':                # 중복 입력 제거
                if status       == 'pending':
                    insert_type = '1'
                    cursor.execute(main_sql, (req_id, insert_type, (unix_time := time.time())))
                    cursor.execute(device_sql, (req_id, tag, ins_pri_ip, id, os_type, ver))
                elif status     == 'shutting-down':
                    insert_type = '2'
                    cursor.execute(main_sql, (req_id, insert_type, (unix_time := time.time())))
                    cursor.execute(device_sql, (req_id, tag, ins_pri_ip, id, os_type, ver))
            else: pass # 이미 데이터가 있음을 슬랙으로 알려주는 것도 괜찮을 듯함. 일단 사용해보고 필요하면.
                
    finally:
        db.close()
