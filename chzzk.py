import requests
import json
import asyncio
import websockets
import pandas as pd
from datetime import datetime
    

class Chzzk:
    def __init__(self, bjid):
        self.bjid = bjid
        
        self.session = requests.session()
        self.channelId = ""
        
        self.accessToken = ""
        self.extraToken = ""

        self.nowTime = datetime.now()

    def getChannelInfo(self):
        try:
            url = f'https://api.chzzk.naver.com/polling/v3/channels/{self.bjid}/live-status'
            self.channelId = self.session.get(url=url).json()['content']['chatChannelId']
            print(f'channelId : {self.channelId}')
        except:
            print("channelId not found(getChannelInfo)")

    def getToken(self):
        try:
            url = f'https://comm-api.game.naver.com/nng_main/v1/chats/access-token?channelId={self.channelId}&chatType=STREAMING'
            token = self.session.get(url=url).json()['content']

            self.accessToken = token['accessToken']
            self.extraToken = token['extraToken']

        except:
            print('Token not found(getToken)')
        
       
#wss://kr-ss1.chat.naver.com/chat
#
class Chat(Chzzk):
    def __init__(self, bjid):
        super().__init__(bjid)
        super().getChannelInfo()
        super().getToken()

        self.socketUrl = 'wss://kr-ss1.chat.naver.com/chat'

        self.reqData = {
            'bdy':{
                'accTkn':self.accessToken,
                'auth':'READ',
                'devName':'Google Chrome/109.0.0.0',
                'devType':2001,
                'libVer':'4.9.3',
                'locale':'ko',
                'osVer':'Linux/',
                'timezone':'Asia/Seoul',
                'uid':None
            },
            'cid':self.channelId,
            'cmd':100,
            'svcid':'game',
            'tid':1,
            'ver':'3'
        }

        self.chatting = []

    async def connect(self):
        async with websockets.connect(self.socketUrl, ping_interval=None) as websocket:
            await websocket.send(json.dumps(self.reqData))
            while (datetime.now() - self.nowTime).seconds < 1800:
                if (datetime.now() - self.nowTime).seconds % 50 == 0:
                    await websocket.send(json.dumps({'ver':"3", 'cmd':10000}))
                    print("===============================================")

                response = await websocket.recv()
                response = json.loads(response)

                if response['cmd'] == 93101:
                    for res in response['bdy']:
                        msg = res['msg']
                        nickname = json.loads(res['profile'])['nickname']
                        self.chatting.append([nickname, msg, datetime.now().strftime('%H:%M:%S')])
                        print(nickname + ' : ' + msg + ' - ' + datetime.now().strftime('%H:%M:%S'))
        
live = '45e71a76e949e16a34764deb962f9d9f'
now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')


go = Chat(live)
crawling = asyncio.run(go.connect())
# crawling.run_until_complete(go.connect())
print("================================")
print(pd.DataFrame(go.chatting).rename(columns={0:'nickname', 1:'msg', 2:'sendTime'}))

response = pd.DataFrame(go.chatting).rename(columns={0:'nickname', 1:'msg', 2:'sendTime'})
filename = f"data/{now}_{live}.csv"
response.to_csv(filename)