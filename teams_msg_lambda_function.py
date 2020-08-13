import json, os, re, boto3, random, time
import pymsteams


def lambda_handler(event, context):
    teams_url = pymsteams.connectorcard(os.environ['teams_urlhook'])
    teams_config(event, context, teams_url)
    
    
def teams_config(event, context, teams_url):
    status = event['detail']['state']
    id = event['detail']['instance-id']
    ec2_vars = []
    
    ec2           = boto3.resource('ec2', region_name = 'ap-northeast-2')
    instance      = ec2.Instance(id)
    imgid         = instance.image_id
    ins_pri_ip    = instance.private_ip_address
    tag           = [ tag['Value'] for tag in instance.tags if tag['Key'] == 'Name' ][0]
    
    image          = ec2.Image(imgid)
    platform       = image.platform_details.split('/')[0]
    imgver         = image.name
    tmp_ver        = re.search(r'(\w+)-(\w+)-(\w+)', imgver).group(1,2)
    ver            = tmp_ver[0] + tmp_ver[1]

    ec2_vars.append('{0} {1} {2} {3} {4} {5}'.format(platform, status, tag, ins_pri_ip, id, ver))
    
    # MSG 
    teams_url.color("<Hex Color Code>")
    teams_url.title('lambda 테스트 메시지입니다.')
    
    teams_section = pymsteams.cardsection()
    teams_section.activityImage('https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/images/instance_lifecycle.png')
    
    teams_url.addLinkButton('LINK', "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/images/instance_lifecycle.png")
    
    teams_url.addSection(teams_section)
    teams_url.text(str(ec2_vars))
    teams_url.send()
