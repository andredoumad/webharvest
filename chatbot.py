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

        if str(socket.gethostname()) == "tr3b":
            self.ws = websocket.WebSocketApp("ws://127.0.0.1:8000/webharvest/",
                        on_message = lambda ws,msg: self.on_message(ws, msg),
                        on_error   = lambda ws,msg: self.on_error(ws, msg),
                        on_close   = lambda ws:     self.on_close(ws),
                        on_open    = lambda ws:     self.on_open(ws))
        else:
            self.ws = websocket.WebSocketApp("wss://stringkeeper.com/webharvest/",
                        on_message = lambda ws,msg: self.on_message(ws, msg),
                        on_error   = lambda ws,msg: self.on_error(ws, msg),
                        on_close   = lambda ws:     self.on_close(ws),
                        on_open    = lambda ws:     self.on_open(ws))

    def check_for_inactive_user(self):
        eventlog("checking for inactive user")
        eventlog('self.last_activity: ' + str(self.last_activity))
        time = datetime.now()
        eventlog('datetime.now: ' + str(time))
        difference = time - self.last_activity
        eventlog('difference: ' + str(difference))
        eventlog('the seconds since last activity is: ' + str(difference.seconds) )
        if difference.seconds >= 30:
            eventlog('the seconds since last activity is too long, shutting down chatbot' )
            self.switchboard.remove_robot_from_user(self.human_email)


    def on_message(self, ws, message):
        eventlog("on_message received message as {}".format(message))
        loaded_dict_data = json.loads(message)
        username = loaded_dict_data.get('username', None)
        if str(username) == str(self.human_email) or self.bool_timer_is_active == False:
            eventlog('updating timer for user status')
            self.last_activity = datetime.now()
            timer = threading.Timer(30.0, self.check_for_inactive_user)
            timer.start()  # after 60 seconds, 'callback' will be called
            self.bool_timer_is_active = True
            # ws.send("hello again")
            # eventlog("sending 'hello again'")

    def on_error(self, ws, error):
        eventlog("on_error received error as {}".format(error))

    def on_close(self, ws):
        eventlog("on_close Connection closed")

    def on_open(self, ws):
        sleep(3)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        text = {
            'message': str('alice on_open ' + str(dt_string)),
            'username': self.name,
            'robot_id': self.name,
            'human': self.human_email
        }
        ws.send(json.dumps(text))

    def on_data(self, ws):
        eventlog("on_data received message as {}".format(message))

    def send_test_message(self):
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
        self.ws.send(json.dumps(text))


    def run_chatbot(self):
        eventlog('hostname: ' + str(socket.gethostname()))
        websocket.enableTrace(True)

        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
        # self.ws.run_forever
        conn_timeout = 5

        while not self.ws.sock.connected and conn_timeout and self.alive:
            sleep(1)
            conn_timeout -= 1

        msg_counter = 0
        while self.ws.sock.connected and self.alive:
            if not self.alive:
                eventlog("I'm " + str(self.name) + " and I'm DEAD!")
                exit()
            else:
                eventlog("I'm " + str(self.name) + " and I'm alive!")
            
            sleep(5)
            self.send_test_message()

        eventlog('setting keep_running to false')
        self.ws.keep_running = False
        eventlog('about to join')
        wst.join()
        eventlog('run_chatbot ends!')