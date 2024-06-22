import requests
import json
import asyncio
import websockets
    

class Chzzk:
    def __init__(self, bjid):
        self.bjid = bjid
        
        self.session = requests.session()
        self.channelId = ""
        
        self.accessToken = ""
        self.extraToken = ""

    def getChannelInfo(self):
        try:
            url = f'https://api.chzzk.naver.com/polling/v2/channels/{self.bjid}/live-status'
            self.channelId = self.session.get(url=url).json()['content']['chatChannelId']
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

    async def connect(self):
        async with websockets.connect(self.socketUrl) as websocket:
            await websocket.send(json.dumps(self.reqData))
            while True:
                response = await websocket.recv()
                response = json.loads(response)
                if response['cmd'] == 93101:
                    for res in response['bdy']:
                        msg = res['msg']
                        nickname = json.loads(res['profile'])['nickname']

                        print(nickname + ' : ' + msg)
        
bighead = 'ca1850b2eceb7f86146695fd9bb9cefc'

go = Chat(bighead)
asyncio.get_event_loop().run_until_complete(go.connect())
