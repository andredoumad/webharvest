import websocket
from time import sleep
import json
from datetime import datetime
import threading
import socket
import logging
from standalone_tools import *

class ChatBot(threading.Thread):
    def __init__(self, name, human_email):
        # self._stopevent = threading.Event(  )
        self.sleep_interval = 1.0
        threading.Thread.__init__(self, name=name)
        self.alive = True
        self.name = name
        self.human_email = human_email
        self.thread = None
        self.last_activity = datetime.now()
        self.switchboard = None
        self.bool_timer_is_active = False
        self.state = 'initialized'
        self.mood = 'helpful'
        self.command = ''
        self.command_input = ''

        if str(socket.gethostname()) == "tr3b":
            self.ws_stringkeeper = websocket.WebSocketApp("ws://127.0.0.1:8000/webharvest/",
                        on_message = lambda ws_stringkeeper,msg: self.on_message_stringkeeper(ws_stringkeeper, msg),
                        on_error   = lambda ws_stringkeeper,msg: self.on_error_stringkeeper(ws_stringkeeper, msg),
                        on_close   = lambda ws_stringkeeper:     self.on_close_stringkeeper(ws_stringkeeper),
                        on_open    = lambda ws_stringkeeper:     self.on_open_stringkeeper(ws_stringkeeper))
        else:
            self.ws_stringkeeper = websocket.WebSocketApp("wss://stringkeeper.com/webharvest/",
                        on_message = lambda ws_stringkeeper,msg: self.on_message_stringkeeper(ws_stringkeeper, msg),
                        on_error   = lambda ws_stringkeeper,msg: self.on_error_stringkeeper(ws_stringkeeper, msg),
                        on_close   = lambda ws_stringkeeper:     self.on_close_stringkeeper(ws_stringkeeper),
                        on_open    = lambda ws_stringkeeper:     self.on_open_stringkeeper(ws_stringkeeper))

        if str(socket.gethostname()) == "tr3b":
            self.ws_spider = websocket.WebSocketApp("ws://127.0.0.1:9090/ws",
                        on_message = lambda ws_spider,msg: self.on_message_spider(ws_spider, msg),
                        on_error   = lambda ws_spider,msg: self.on_error_spider(ws_spider, msg),
                        on_close   = lambda ws_spider:     self.on_close_spider(ws_spider),
                        on_open    = lambda ws_spider:     self.on_open_spider(ws_spider))
        else:
            self.ws_spider = websocket.WebSocketApp("ws://172.26.5.185:9090/ws",
                        on_message = lambda ws_spider,msg: self.on_message_spider(ws_spider, msg),
                        on_error  = lambda ws_spider,msg: self.on_error_spider(ws_spider, msg),
                        on_close   = lambda ws_spider:     self.on_close_spider(ws_spider),
                        on_open    = lambda ws_spider:     self.on_open_spider(ws_spider))


    def check_for_inactive_user(self):
        eventlog("checking for inactive user")
        eventlog('self.last_activity: ' + str(self.last_activity))
        time = datetime.now()
        eventlog('datetime.now: ' + str(time))
        difference = time - self.last_activity
        eventlog('difference: ' + str(difference))
        eventlog('the seconds since last activity is: ' + str(difference.seconds) )
        if difference.seconds >= 3600:
            eventlog('the seconds since last activity is too long, shutting down chatbot' )
            self.switchboard.remove_robot_from_user(self.human_email)


    # SPIDER
    def on_message_spider(self, ws_spider, message):
        eventlog("on_message received message as {}".format(message))
        loaded_dict_data = json.loads(message)
        username = loaded_dict_data.get('username', None)
        if str(username) == str(self.human_email) or self.bool_timer_is_active == False:
            eventlog('updating timer for user status')
            self.last_activity = datetime.now()
            timer = threading.Timer(3600.0, self.check_for_inactive_user)
            timer.start()  # after 60 seconds, 'callback' will be called
            self.bool_timer_is_active = True
            # ws_stringkeeper.send("hello again")
            # eventlog("sending 'hello again'")
        
        if self.state == 'initialized':
            if self.message_is_salutation(message):
                self.send_message_stringkeeper('Hello! How can I help you today?')
                self.state = ('looking_for_command')

        if self.state == 'looking_for_command':
            if self.message_is_search(message):
                self.send_message_stringkeeper('What would you like to search for?')
                self.state = ('waiting_for_search_keys_input')

        if self.state == 'waiting_for_search_keys_input':
            if self.message_is_search(message):
                self.send_message_stringkeeper("I understand you'd like to search for: ")
                self.send_message_stringkeeper(str(message))
                self.command_input = str(message)
                self.send_message_stringkeeper("Is that correct?")

            if self.message_user_agrees(message):
                self.send_message_stringkeeper("Alright, I'm going to begin the search for emails related to your keys and I'll show you what I'm finding as I find it.")
                self.send_message_stringkeeper(str(message))
                self.state = ('crawling_search_key_input')
            else:
                self.send_message_stringkeeper("I have canceled that job. I am designed to search for emails related to your search. What would you like to search for?")
                self.state = 'waiting_for_search_keys_input'

        if self.state == 'crawling_search_key_input':
            if self.mood != 'busy':
                if self.message_is_stop(message):
                    self.send_message_stringkeeper("I'm sorry dave, I can't do that right now.")
                    self.mood = 'busy'
            else:
                if self.message_is_stop(message):
                    self.send_message_stringkeeper("I'm only programmed to run this job for a few minutes and when I'm done I'll be ready for further commands.")
                    self.mood = 'busy'

    def send_message_spider(self, message):
        text = {
            'message': message,
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        self.ws_spider.send(json.dumps(text))

    def on_error_spider(self, ws_spider, error):
        eventlog("on_error received error as {}".format(error))

    def on_close_spider(self, ws_spider):
        eventlog("on_close Connection closed")

    def on_open_spider(self, ws_spider):
        sleep(1)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        text = {
            'message': str('alice on_open ' + str(dt_string)),
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        ws_spider.send(json.dumps(text))


    # STRINGKEEPER
    def on_message_stringkeeper(self, ws_stringkeeper, message):
        eventlog("on_message received message as {}".format(message))
        loaded_dict_data = json.loads(message)
        username = loaded_dict_data.get('username', None)
        if str(username) == str(self.human_email) or self.bool_timer_is_active == False:
            eventlog('updating timer for user status')
            self.last_activity = datetime.now()
            timer = threading.Timer(3600.0, self.check_for_inactive_user)
            timer.start()  # after 60 seconds, 'callback' will be called
            self.bool_timer_is_active = True
            # ws_stringkeeper.send("hello again")
            # eventlog("sending 'hello again'")
        
        if self.state == 'initialized':
            if self.message_is_salutation(message):
                self.send_message_stringkeeper('Hello! How can I help you today?')
                self.state = ('looking_for_command')

        if self.state == 'looking_for_command':
            if self.message_is_search(message):
                self.send_message_stringkeeper('What would you like to search for?')
                self.state = ('waiting_for_search_keys_input')

        if self.state == 'waiting_for_search_keys_input':
            if self.message_is_search(message):
                self.send_message_stringkeeper("I understand you'd like to search for: ")
                self.send_message_stringkeeper(str(message))
                self.command_input = str(message)
                self.send_message_stringkeeper("Is that correct?")

            if self.message_user_agrees(message):
                self.send_message_stringkeeper("Alright, I'm going to begin the search for emails related to your keys and I'll show you what I'm finding as I find it.")
                self.send_message_stringkeeper(str(message))
                self.state = ('crawling_search_key_input')
            else:
                self.send_message_stringkeeper("I have canceled that job. I am designed to search for emails related to your search. What would you like to search for?")
                self.state = 'waiting_for_search_keys_input'

        if self.state == 'crawling_search_key_input':
            if self.mood != 'busy':
                if self.message_is_stop(message):
                    self.send_message_stringkeeper("I'm sorry dave, I can't do that right now.")
                    self.mood = 'busy'
            else:
                if self.message_is_stop(message):
                    self.send_message_stringkeeper("I'm only programmed to run this job for a few minutes and when I'm done I'll be ready for further commands.")
                    self.mood = 'busy'

    def message_is_salutation(self, message):
        message = message.lower()
        if message.find('hello') != -1: 
            return True
        elif message.find('hi') != -1: 
            return True
        elif message.find('ok') != -1: 
            return True
        elif message.find('hey') != -1: 
            return True
        else:
            return False
        
    def message_is_search(self, message):
        message = message.lower()
        if message.find('search') != -1: 
            return True
        elif message.find('find') != -1: 
            return True
        else:
            return False
        
    def message_user_agrees(self, message):
        message = message.lower()
        if message.find('yes') != -1: 
            return True
        elif message.find('ok') != -1: 
            return True
        elif message.find('agree') != -1: 
            return True
        elif message.find('yeah') != -1: 
            return True
        elif message.find('alright') != -1: 
            return True
        elif message.find('yup') != -1: 
            return True
        else:
            return False

    def message_is_stop(self, message):
        message = message.lower()
        if message.find('stop') != -1: 
            return True
        elif message.find('halt') != -1: 
            return True
        elif message.find('exit') != -1: 
            return True
        elif message.find('cancel') != -1: 
            return True
        elif message.find('wait') != -1: 
            return True
        elif message.find('no') != -1: 
            return True
        else:
            return False

    def on_error_stringkeeper(self, ws_stringkeeper, error):
        eventlog("on_error received error as {}".format(error))

    def on_close_stringkeeper(self, ws_stringkeeper):
        eventlog("on_close Connection closed")

    def on_open_stringkeeper(self, ws_stringkeeper):
        # sleep(3)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        text = {
            'message': str('alice on_open ' + str(dt_string)),
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        ws_stringkeeper.send(json.dumps(text))

    def on_data_stringkeeper(self, ws_stringkeeper):
        eventlog("on_data received message as {}".format(message))

    def send_message_stringkeeper(self, message):
        text = {
            'message': message,
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        self.ws_stringkeeper.send(json.dumps(text))

    def send_test_message_stringkeeper(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        text = str('hi there, im Alice, the time is ' + str(dt_string))
        eventlog(text)
        text = {
            'message': text,
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        self.ws_stringkeeper.send(json.dumps(text))

    def run_chatbot(self):
        eventlog('hostname: ' + str(socket.gethostname()))
        websocket.enableTrace(True)

        ws_stringkeeper_thread = threading.Thread(target=self.ws_stringkeeper.run_forever)
        ws_stringkeeper_thread.daemon = True
        ws_stringkeeper_thread.start()
        # self.ws_stringkeeper.run_forever
        conn_timeout = 5

        while not self.ws_stringkeeper.sock.connected and conn_timeout and self.alive:
            sleep(1)
            conn_timeout -= 1

        msg_counter = 0
        while self.ws_stringkeeper.sock.connected and self.alive:
            if not self.alive:
                eventlog("I'm " + str(self.name) + " and I'm DEAD!")
                exit()
            else:
                eventlog(
                "Name: " + str(self.name) + 
                " State: " + str(self.state) +
                " Mood: " + str(self.mood) +
                " Command: " + str(self.command) +
                " Command_Input: " + str(self.command_input)
                )
            sleep(1)
            # self.send_test_message_stringkeeper()

        eventlog('setting keep_running to false')
        self.ws_stringkeeper.keep_running = False
        eventlog('about to join')
        ws_stringkeeper_thread.join()
        eventlog('run_chatbot ends!')