import requests
import json
import asyncio
import websockets
import pandas as pd

from datetime import datetime
from pytz import timezone
    

class Chzzk:
    def __init__(self, bjid):
        self.bjid = bjid
        
        self.session = requests.session()
        self.channelId = ""
        
        self.accessToken = ""
        self.extraToken = ""

        self.nowTime = datetime.now(timezone('Asia/Seoul'))

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
            },
            'cid':self.channelId,
            'cmd':100,
            'svcid':'game',
            'tid':1,
            'ver':'3'
        }

        self.chatting = []

    async def connect(self):
        async with websockets.connect(self.socketUrl, ping_interval=60) as websocket:
            await websocket.send(json.dumps(self.reqData))
            #(datetime.now(timezone('Asia/Seoul')) - self.nowTime).seconds < 3600:
            while True:
                now = datetime.now(timezone('Asia/Seoul'))

                response = await websocket.recv()
                response = json.loads(response)

                if response['cmd'] == 0:
                    await websocket.send(json.dumps({'ver':"3", 'cmd':10000}))
                    print("===============================================")
                    continue

                if response['cmd'] == 93101:
                    for res in response['bdy']:
                        msg = res['msg']
                        nickname = json.loads(res['profile'])['nickname']
                        self.chatting.append([nickname, msg, now.strftime('%Y-%m-%d_%H:%M:%S')])
                        print(nickname + ' : ' + msg + ' - ' + now.strftime('%Y-%m-%d_%H:%M:%S'))

live = '75cbf189b3bb8f9f687d2aca0d0a382b' #한동숙
now = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d_%H:%M:%S')


go = Chat(live)
asyncio.get_event_loop().run_until_complete(go.connect())
#asyncio.run(go.connect())

print("================================")
print(pd.DataFrame(go.chatting).rename(columns={0:'nickname', 1:'msg', 2:'sendTime'}))

response = pd.DataFrame(go.chatting).rename(columns={0:'nickname', 1:'msg', 2:'sendTime'})
filename = f"python/data/{now}_{live}.csv"
response.to_csv(filename, index=False)