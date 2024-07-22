import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# API 키를 설정합니다.
API_KEY = 'apikey'

# YouTube Data API 클라이언트를 빌드합니다.
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 라이브 스트림 ID를 입력합니다.
live_chat_id = 'LIVE_CHAT_ID'

# 라이브 채팅 메시지를 가져오는 함수입니다.
def get_live_chat_messages(live_chat_id):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part='id,snippet,authorDetails',
    ).execute()
    return response['items']

# 라이브 스트림의 ID를 가져오는 함수입니다.
def get_live_chat_id(video_id):
    response = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    ).execute()
    live_chat_id = response['items'][0]['liveStreamingDetails']['activeLiveChatId']
    return live_chat_id

# 실시간으로 채팅 메시지를 크롤링합니다.
def main():
    video_id = '1YvRu7O6k8I'  # YouTube 비디오 ID를 입력합니다.
    live_chat_id = get_live_chat_id(video_id)
    
    while True:
        messages = get_live_chat_messages(live_chat_id)
        for message in messages:
            author = message['authorDetails']['displayName']
            text = message['snippet']['displayMessage']
            print(f'{author}: {text}')

if __name__ == '__main__':
    main()
