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
        self.To = ''
        self.From = ''
        self.previous_message_bot_message_type = ''
        self.user_search_keys = ''

        if str(socket.gethostname()) == "tr3b":
            eventlog('SETTING UP CONNECTION TO LOCAL WEBSERVER!')
            self.ws_stringkeeper = websocket.WebSocketApp("ws://127.0.0.1:8000/webharvest/",
                        on_message = lambda ws_stringkeeper,msg: self.on_message_stringkeeper(ws_stringkeeper, msg),
                        on_error   = lambda ws_stringkeeper,msg: self.on_error_stringkeeper(ws_stringkeeper, msg),
                        on_close   = lambda ws_stringkeeper:     self.on_close_stringkeeper(ws_stringkeeper),
                        on_open    = lambda ws_stringkeeper:     self.on_open_stringkeeper(ws_stringkeeper))
        else:
            eventlog('SETTING UP CONNECTION TO REMOTE WEBSERVER!')
            self.ws_stringkeeper = websocket.WebSocketApp("wss://stringkeeper.com/webharvest/",
                        on_message = lambda ws_stringkeeper,msg: self.on_message_stringkeeper(ws_stringkeeper, msg),
                        on_error   = lambda ws_stringkeeper,msg: self.on_error_stringkeeper(ws_stringkeeper, msg),
                        on_close   = lambda ws_stringkeeper:     self.on_close_stringkeeper(ws_stringkeeper),
                        on_open    = lambda ws_stringkeeper:     self.on_open_stringkeeper(ws_stringkeeper))

        # if str(socket.gethostname()) == "tr3b":
        #     eventlog('SETTING UP CONNECTION TO LOCAL SPIDER!')
        #     self.ws_spider = websocket.WebSocketApp("ws://localhost:9090/ws",
        #                 on_message = lambda ws_spider,msg: self.on_message_spider(ws_spider, msg),
        #                 on_error   = lambda ws_spider,msg: self.on_error_spider(ws_spider, msg),
        #                 on_close   = lambda ws_spider:     self.on_close_spider(ws_spider),
        #                 on_open    = lambda ws_spider:     self.on_open_spider(ws_spider))
        # else:
        eventlog('SETTING UP CONNECTION TO REMOTE SPIDER!')
        # self.ws_spider = websocket.WebSocketApp("ws://44.233.102.110:9090/ws", # spider_0
        self.ws_spider = websocket.WebSocketApp("ws://citadel.blackmesanetwork.com:9090/ws", # citadel
                    on_message = lambda ws_spider,msg: self.on_message_spider(ws_spider, msg),
                    on_error   = lambda ws_spider,msg: self.on_error_spider(ws_spider, msg),
                    on_close   = lambda ws_spider:     self.on_close_spider(ws_spider),
                    on_open    = lambda ws_spider:     self.on_open_spider(ws_spider))
        
        # self.send_spider_test_message()


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
        eventlog('ON MESSAGE SPIDER TRIGGERED!')
        # eventlog("on_message received message as {}".format(message))
        eventlog('message: ' + str(message))
        loaded_dict_data = json.loads(message)
        message = loaded_dict_data.get('message', None)
        command = loaded_dict_data.get('command', None)
        robot_id = loaded_dict_data.get('robot_id', None)
        human = loaded_dict_data.get('human', None)

        #THIS IS NOT BEING USED 

        #THIS WHOLE FUNCTION IS NOT BEING USED. BECAUSE -- POST to the VIEW on strinkeeper is sending messages to the chatbot from the spider.
        if command == 'print':
            self.send_message_stringkeeper(message)
        
        if command == 'update_state':
            self.state = message


    # SPIDER
    def send_message_spider(self, message, command):
        eventlog('ON SEND SPIDER TRIGGERED!')
        eventlog('message: ' + str(message))
        eventlog('command: ' + str(command))
        text = {
            'message': message,
            'command': command,
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        self.ws_spider.send(json.dumps(text))

    # SPIDER
    def on_error_spider(self, ws_spider, error):
        eventlog('ON ERROR SPIDER TRIGGERED!')
        eventlog("on_error received error as {}".format(error))

    # SPIDER
    def on_close_spider(self, ws_spider):
        eventlog('ON CLOSE SPIDER TRIGGERED!')
        eventlog("on_close Connection closed")

    # SPIDER
    def send_spider_test_message(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        text = str('Hello from Alice chatbot ' + str(dt_string))
        eventlog(text)
        text = {
            'message': text,
            'username': 'Alice',
            'robot_id': 'Alice_0',
            'human': 'dante@stringkeeper.com'
        }
        self.ws_spider.send(json.dumps(text))

    # SPIDER
    def on_open_spider(self, ws_spider):
        eventlog('ON OPEN SPIDER TRIGGERED!')

    # STRINGKEEPER
    def on_message_stringkeeper(self, ws_stringkeeper, message):

        eventlog("on_message received message as {}".format(message))
        loaded_dict_data = json.loads(message)
        # eventlog('loaded_dict_data: ' + str(loaded_dict_data))
        robot_id = None
        robot_id = loaded_dict_data.get('robot_id', None)
        # eventlog('robot_id: ' + str(robot_id))


        self.To = None
        self.From = None
        self.To = loaded_dict_data.get('To', None)
        # eventlog('To: ' + str(self.To))
        message = loaded_dict_data.get('message', None)
        command = loaded_dict_data.get('command', None)
        if command == 'update_state':
            self.state = message

        # eventlog('message: ' + str(message))
        self.From = loaded_dict_data.get('From', None)
        # eventlog('From: ' + str(self.From))

        if self.From != self.name:
            username = loaded_dict_data.get('username', None)

            if str(username) == str(self.human_email) or self.bool_timer_is_active == False:
                eventlog('updating timer for user status')
                self.last_activity = datetime.now()
                timer = threading.Timer(3600.0, self.check_for_inactive_user)
                timer.start()  # after 60 seconds, 'callback' will be called
                self.bool_timer_is_active = True
            
            # check for clear screen message
            self.robot_command_clear(message)


            if self.state == 'looking_for_command' or self.state == 'initialized':
                eventlog('\n checking for search commands \n')
                complete = False
                complete = self.message_search(message)
                if complete:
                    pass
                elif self.message_is_salutation(message):
                    self.send_message_stringkeeper(random("salutation"))
                else:
                    self.message_search('search ' + message)
                    
                    

            elif self.state == 'enter_search_keys':
                eventlog('\n checking for search input keys \n')
                self.send_message_stringkeeper(random("chat/out/echo_input") + message)
                self.command_input = str(message)
                self.send_message_stringkeeper(random("chat/out/question/confirm"))
                self.state = ('confirm')

            elif self.state == 'confirm':
                if self.message_user_agrees(message):
                    self.send_message_stringkeeper(random("chat/out/starting_search"))
                    self.send_message_spider(self.command_input, 'search')
                    self.state = ('crawling_search_key_input')
                else:
                    self.send_message_stringkeeper(random("chat/out/stopping_work"))
                    self.state = 'initialized'
            elif self.state == 'crawling_search_key_input':
                if self.message_is_stop(message):
                    self.send_message_stringkeeper(random("chat/out/stopping_work"))
                    eventlog('STOPPING SEARCH')
                    eventlog('STOPPING SEARCH')
                    eventlog('STOPPING SEARCH')
                    self.send_message_spider(self.command_input, 'stop_search')
                    self.state = 'initialized'
                # elif self.message_is_spider_log(message):
                #     self.send_message_spider('spider_log_update_request', 'spider_log')



    # STRINGKEEPER
    def send_message_stringkeeper(self, message):
        # eventlog('To: ' + str(self.human_email))
        # eventlog('message: ' + str(message))

        text = {
            'To': self.human_email,
            'From': self.name,
            'message': message,
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        self.ws_stringkeeper.send(json.dumps(text))

    # STRINGKEEPER
    def send_robot_command_stringkeeper(self, robot_command=None, message=None):
        # eventlog('To: ' + str(self.human_email))
        # eventlog('robot_command: ' + str(robot_command))
        # eventlog('message: ' + str(message))
        
        text = {
            'To': self.human_email,
            'From': self.name,
            'message': message,
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email,
            'robot_command': robot_command
        }
        self.ws_stringkeeper.send(json.dumps(text))

    # STRINGKEEPER
    def robot_command_clear(self, message):
        message = message.lower()
        if message.find('clear') != -1:
            eventlog('sending clear command')
            self.send_robot_command_stringkeeper(robot_command='clear', message='clear')

    # STRINGKEEPER
    def send_stringkeeper_manual(self):
        self.send_message_stringkeeper('"clear" removes old text from screen.')
        self.send_message_stringkeeper('"search" define and execute a search.')
        # self.send_message_stringkeeper('Reply with "help" for instructions.')

    # STRINGKEEPER
    def UpdatePreviousMessageBotMessageType(self):
        previous_frame = inspect.currentframe().f_back
        (filename, line_number,  function_name, lines, index) = inspect.getframeinfo(previous_frame)
        self.previous_message_bot_message_type = str(function_name)

    # STRINGKEEPER
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

    # STRINGKEEPER
    def message_search(self, message):
        eventlog('message_search')
        message = message.lower()
        prompt_for_search_keys = False
        search_keys = None
        triggered = False
        if message == 'search' or message == 'find':
            eventlog('FOUND SEARCH TRIGGER')
            prompt_for_search_keys = True

        elif message.find('search') != -1:
            search_keys = message
        elif message.find('find') != -1:
            search_keys = message
        elif message.find('look') != -1:
            search_keys = message

        # found search commands with search keys
        if search_keys != None:
            # search_keys = search_keys.replace('for', '')
            self.send_message_stringkeeper(random("chat/out/echo_input") + search_keys)
            self.command_input = str(search_keys)
            self.send_message_stringkeeper(random("chat/out/question/confirm"))
            self.state = ('confirm')
            triggered = True

        # found only search commands
        if prompt_for_search_keys == True:
            self.send_message_stringkeeper(random("chat/out/question/search/enter_search_keys"))
            self.state = ('enter_search_keys')
            # self.UpdatePreviousMessageBotMessageType()
            triggered = True

        if triggered == True:
            self.UpdatePreviousMessageBotMessageType()
            return True
        else:
            return False

    # STRINGKEEPER
    def message_user_agrees(self, message):
        message = message.lower()
        if message.find('yes') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('ok') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('agree') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('yeah') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('alright') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('yup') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        else:
            return False

    # STRINGKEEPER
    def message_is_stop(self, message):
        message = message.lower()
        if message.find('spider_log') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        else:
            return False


    # STRINGKEEPER
    def message_is_stop(self, message):
        message = message.lower()
        if message.find('stop') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('halt') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('exit') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('cancel') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('wait') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        elif message.find('no') != -1: 
            self.UpdatePreviousMessageBotMessageType()
            return True
        else:
            return False

    # STRINGKEEPER
    def on_error_stringkeeper(self, ws_stringkeeper, error):
        eventlog("on_error received error as {}".format(error))

    # STRINGKEEPER
    def on_close_stringkeeper(self, ws_stringkeeper):
        eventlog("on_close Connection closed")

    # STRINGKEEPER
    def on_open_stringkeeper(self, ws_stringkeeper):
        self.send_message_stringkeeper('Welcome!')

    # STRINGKEEPER
    def on_data_stringkeeper(self, ws_stringkeeper):
        eventlog("on_data received message as {}".format(message))



    def run_chatbot(self):
        eventlog('hostname: ' + str(socket.gethostname()))
        websocket.enableTrace(True)

        ws_stringkeeper_thread = threading.Thread(target=self.ws_stringkeeper.run_forever)
        ws_stringkeeper_thread.daemon = True
        ws_stringkeeper_thread.start()

        ws_spider_thread = threading.Thread(target=self.ws_spider.run_forever)
        ws_spider_thread.daemon = True
        ws_spider_thread.start()
        # self.ws_stringkeeper.run_forever
        conn_timeout = 5
        try:
            while not self.ws_stringkeeper.sock.connected and conn_timeout and self.alive:
                sleep(1)
                conn_timeout -= 1
        except:
            eventlog('chatbot disconnected!')
            pass

        msg_counter = 0

        previous_string = ''
        try:
            while self.ws_stringkeeper.sock.connected and self.alive:
                if not self.alive:
                    eventlog("I'm " + str(self.name) + " and I'm DEAD!")
                    exit()
                else:
                    message = str(
                    "Name: " + str(self.name) + 
                    " Human: " + str(self.human_email) +
                    " To: " + str(self.To) +
                    " From: " + str(self.From) +
                    " State: " + str(self.state) +
                    " Mood: " + str(self.mood) +
                    " Command: " + str(self.command) +
                    " Command_Input: " + str(self.command_input)
                    )

                    if len(previous_string) != len(message):
                        if previous_string != message:
                            eventlog(message)
                            previous_string = message

                    sleep(3)
                # self.send_test_message_stringkeeper()
        except:
            eventlog('chatbot disconnected!')
        
        self.alive = False
        eventlog('setting keep_running to false')
        self.ws_stringkeeper.keep_running = False
        self.ws_spider.keep_running = False
        eventlog('about to join')
        ws_stringkeeper_thread.join()
        ws_spider_thread.join()
        eventlog('run_chatbot ends!')



if __name__ == "__main__":
    eventlog(random('salutation'))