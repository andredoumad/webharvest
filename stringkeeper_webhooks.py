import json
import requests
from datetime import datetime
import asyncio
import logging
import websockets
logging.basicConfig(level=logging.INFO)

class WebHarvestWorker:

    def __init__(self, name):
        self.name = name
        self.api_url = 'https://stringkeeper.com/webhooks/webharvest/'
        # self.api_url = 'http://127.0.0.1:8000/webhooks/webharvest/'
        self.user = ''
        self.chat = ''
        self.response = None

    def initialize(self):
        # post
        payload = {}
        self.post(payload)
        data = self.response.json()
        self.user = data['user']
        print('initialized for user: ' + str(self.user))

    def post(self, payload):
        updated_dictionary = payload
        updated_dictionary['user'] = self.user
        print('updated_dictionary = ' + str(updated_dictionary))
        self.response = requests.post(self.api_url, data=updated_dictionary)

        print('reponse object: ' + str(self.response))
        print('reponse JSON: ' + str(self.response.json()))

    def chat_message(self, message):
        self.post({
            'chat_message': str(message)
        })

worker = WebHarvestWorker('Alice')
print(worker.name)

worker.initialize()
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
worker.chat_message(str('My name is ' + str(worker.name) + '. The time is: ' + dt_string + '.'))
print('response: ' + str(worker.response))
print('response json: ' + str(worker.response.json()))



# async def command_receiver():
#     async with websockets.connect('ws://127.0.0.1:80/webharvest/') as websocket:
#         while True:
#             message = await websocket.recv()
#             await websocket.send("Received the command '{message}'")
#             if message == "start":
#                 print('received message start')
#             elif message == "stop":
#                 print('received message stop')
#             else:
#                 await websocket.send("Unknown command")     


# # asyncio.get_event_loop().run_until_complete(command_receiver())
# asyncio.get_event_loop().run_until_complete(command_receiver())