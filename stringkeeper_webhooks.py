import json
import requests


class WebHarvestWorker:

    def __init__(self, name):
        self.name = name
        self.api_url = 'https://stringkeeper.com/webhooks/webharvest/'
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
worker.chat_message(str('My name is ' + str(worker.name) + '.'))
print('response: ' + str(worker.response))
print('response json: ' + str(worker.response.json()))