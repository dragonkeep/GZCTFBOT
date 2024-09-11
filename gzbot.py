import argparse 
from datetime import datetime, timezone, timedelta
import requests
import urllib3
import  asyncio
import time
import json
import sys
urllib3.disable_warnings()
class Config():
    def __init__(self,args):
        self.url = args.url
        self.notice = args.notice
        self.port = args.port
        self.race_id=args.id    
class Message():
    def __init__(self,config):
        self.config = config
        self.session = requests.Session()

    def process_time(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def get_notice(self):
        url =self.config.url + f"/api/game/{self.config.race_id}/notices"
        try:
            response=requests.get(url,verify=False)
            if response.text=='[]':
                sys.exit()
            return json.loads(response.text)
        except:
            sys.exit(f"\033[31m[{self.process_time()}] [ERROR]: Please add a new challenge and use it! :(\033[0m")
    def send_message(self,msg):
        try:
            send_url=f'http://127.0.0.1:{self.config.port}/send_group_msg?group_id={self.config.notice}&message={msg}'
            self.session.get(send_url)
            print(f'\033[32m[{self.process_time()}] [SEND] Sending message to {self.config.notice_group_id}\033[0m')
        except requests.exceptions.ConnectionError:
            sys.exit(f"\033[31m[{self.process_time()}] [ERROR] Connection error. Check port or address.\033[0m")

class Notice():
    def __init__(self,config):
        self.config=config
        self.message=Message(config)    
        self.notice_len = 0
    def get_notice(self):
        return  self.message.get_notice()
    def handle_notice(self):
        blood_types = ['FirstBlood', 'SecondBlood', 'ThirdBlood']
        notices = self.get_notice()
        blood_notices=[n for n in notices if n['type'] in blood_types]
        for notice in blood_notices:
            blood_type=notice['type']
            msg=f"【{blood_type} 播报】\n内容：{notice['content']}\n时间：{self.message.process_time()}"
            self.message.send_message(msg)

async def send_message_notice(notice):
    try:
        while True:
            print(f'\033[33m[{notice.message.process_time()}] [INFO]: Waiting for data...\033[0m')
            notice.handle_notice()
            await asyncio.sleep(3)
    except KeyboardInterrupt:
        print(f'\033[31m[{notice.message.process_time()}] [ERROR]: Trying to exit!!!\033[0m')


async def runner(config):
    notice = Notice(config)
    await asyncio.gather(
        send_message_notice(notice)
    )

def main(): 
    BANNER = """\033[01;34m\
    
  _____  ______    _____ ___________  ______       _   
 |  __ \|___  /_ _/  __ \_   _|  ___| | ___ \     | |  
 | |  \/   / /(_|_) /  \/ | | | |_    | |_/ / ___ | |_  `
 | | __   / /     | |     | | |  _|   | ___ \/ _ \| __|
 | |_\ \./ /____ _| \__/\ | | | |     | |_/ / (_) | |_    \033[0m\033[4;37m%s\033[0m
  \____/\_____(_|_)\____/ \_/ \_|     \____/ \___/ \__|   \033[0m\033[4;37m%s\033[0m\n
    """ % ("Author: Dragonkeep", "Version: v0.1.1")
    print(BANNER)
    parser = argparse.ArgumentParser(description="GZ::CTF QQ Bot")
    parser.add_argument('--url', 
                        required=True,
                        help="platform url")
    parser.add_argument('--notice', 
                        required=True,
                        help="qq notice Group")
    parser.add_argument('--id', 
                        required=True,
                        help="race id")
    parser.add_argument('--port', 
                        required=True,
                        help="cq port")
    parser.add_argument('--events', 
                        help="qq detail group (optional)")
    parser.add_argument('--cookie', 
                        help="administrator cookie")
    args = parser.parse_args()
    config = Config(args)
    asyncio.run(runner(config))
if __name__=="__main__":
    main()