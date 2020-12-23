import websocket
from time import sleep
import json
from datetime import datetime
import threading
import socket
import logging
from standalone_tools import *
from chatbot import ChatBot

# version 2
class WebHarvest:
    def __init__(self, name):
        self.name = name
        self.target_url = ''
        # if str(socket.gethostname()) != "tr3b" or str(socket.gethostname()) == "gman":
        #     # self.target_url = 'wss://stringkeeper.com/webharvest/'
        #     self.target_url = 'wss://stringkeeper.com/webharvest/'
        #     self.ws = websocket.WebSocketApp("wss://stringkeeper.com/webharvest/",
        #                 on_message = lambda ws,msg: self.on_message(ws, msg),
        #                 on_error   = lambda ws,msg: self.on_error(ws, msg),
        #                 on_close   = lambda ws:     self.on_close(ws),
        #                 on_open    = lambda ws:     self.on_open(ws))

        # else:
        #     self.target_url = 'ws://127.0.0.1:8000/webharvest/'
        #     self.ws = websocket.WebSocketApp("ws://127.0.0.1:8000/webharvest/",
        #                 on_message = lambda ws,msg: self.on_message(ws, msg),
        #                 on_error   = lambda ws,msg: self.on_error(ws, msg),
        #                 on_close   = lambda ws:     self.on_close(ws),
        #                 on_open    = lambda ws:     self.on_open(ws))

        # self.target_url = 'wss://stringkeeper.com/webharvest/'
        # self.ws = websocket.WebSocketApp("wss://stringkeeper.com/webharvest/",
        #             on_message = lambda ws,msg: self.on_message(ws, msg),
        #             on_error   = lambda ws,msg: self.on_error(ws, msg),
        #             on_close   = lambda ws:     self.on_close(ws),
        #             on_open    = lambda ws:     self.on_open(ws))

        self.target_url = 'wss://127.0.0.1:8000/webharvest/'
        self.ws = websocket.WebSocketApp("wss://127.0.0.1:8000/webharvest/",
                    on_message = lambda ws,msg: self.on_message(ws, msg),
                    on_error   = lambda ws,msg: self.on_error(ws, msg),
                    on_close   = lambda ws:     self.on_close(ws),
                    on_open    = lambda ws:     self.on_open(ws))


        self.user_robot_assignment_dict = {}

    def on_message(self, ws, message):

        dictionary_message = message
        loaded_dict_data = json.loads(message)
        robot_command = loaded_dict_data.get('robot_command', None)

        if robot_command == 'get_active_and_inactive_users':
            inactive_users_string = loaded_dict_data.get('inactive_users', None)
            active_users_string = loaded_dict_data.get('active_users', None)

            inactive_users_dict = json.loads(inactive_users_string)
            eventlog(str('TIME: ' + get_time_string()))
            for key, value in inactive_users_dict.items():
                eventlog(str('inactive_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))
                robot = self.user_robot_assignment_dict.get(str(key))
                if robot != None:
                    eventlog(str("self.user_robot_assignment_dict.get(str(key)) != None: " ))
                    eventlog('key: ' + str(key))
                    eventlog('robot: ' + str(robot))
                    self.remove_robot_from_user(str(key))

            active_users_dict = json.loads(active_users_string)

            for key, value in active_users_dict.items():
                eventlog(str('active_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))

                # if value == None:
                if self.user_robot_assignment_dict.get(str(key)) == None:
                    eventlog(str('user: ' + str(key) + ' is active and needs a robot!'))
                    message = loaded_dict_data.get('message', None)
                    eventlog('message: ' + str(message))
                    self.assign_robot_to_user(str(key), dictionary_message)
        
        elif robot_command == 'update_user_status':
            eventlog('triggered updated_user_status!')
            human = loaded_dict_data.get('human', None)
            eventlog('human: ' + str(human))
            message = loaded_dict_data.get('message', None)
            eventlog('message: ' + str(message))
            
            if self.user_robot_assignment_dict.get(str(human)) == None:
                eventlog(str('user: ' + str(human) + ' is active and needs a robot!'))
                self.assign_robot_to_user(str(human), dictionary_message)

    def on_error(self, ws, error):
        eventlog(f"self.target_url: {self.target_url}")
        eventlog("on_error received error as {}".format(error))

    def on_close(self, ws):
        eventlog('self.target_url: {}'.format(self.target_url))
        eventlog("on_close Connection closed")

    def on_open(self, ws):
        eventlog('self.target_url: '.format(self.target_url))
        sleep(3)

        text = {
            'robot_id': 'webharvest_robot_router',

        }
        ws.send(json.dumps(text))

    # def on_data(self, ws):
    #     print("on_data received message as {}".format(message))

    def get_update(self, ws):
        text = {
            'robot_id': 'webharvest_robot_router',
            'robot_command': 'get_active_and_inactive_users',
        }
        ws.send(json.dumps(text))

    def assign_robot_to_user(self, human, message):
        eventlog('assign_robot_to_user....')
        thread = self.user_robot_assignment_dict.get(human)
        eventlog('thread: ' + str(thread))

                
        if thread == None:
            eventlog('human not found...')
            robot = ChatBot('Alice', str(human), message)
            chatbot_thread = threading.Thread(target=robot.run_chatbot)
            chatbot_thread.daemon = True
            chatbot_thread.start()
            robot.thread = chatbot_thread
            robot.switchboard = self
            self.user_robot_assignment_dict[human] = robot
            robot.spider_ip = '127.0.0.1'
            robot.spider_port = '9090'
        
        thread = self.user_robot_assignment_dict.get(human)
        eventlog('thread: ' + str(thread))
        # robot.run_chatbot()

    def remove_robot_from_user(self, human):
        eventlog('remove_robot_from_user....')
        robot = self.user_robot_assignment_dict.get(human)
        eventlog('robot to remove: ' + str(robot))
        if robot == None:
            eventlog('human not found...')
            eventlog('this should only fire if a human has a bot...')
            exit()

        self.user_robot_assignment_dict.get(human).alive = False
        self.user_robot_assignment_dict[human] = None
        eventlog('robot None: ' + str(self.user_robot_assignment_dict.get(human)))

    def set_all_users_to_inactive(self):
        text = {
            'robot_id': 'webharvest_robot_router',
            'robot_command': 'set_all_users_to_inactive'
        }
        self.ws.send(json.dumps(text))

    def subscribe_to_user_updates(self):
        eventlog('subscribe_to_user_updates')
        text = {
            'robot_id': 'webharvest_robot_router',
            'robot_command': 'subscribe_to_user_status_updates'
        }
        self.ws.send(json.dumps(text))



def run_webharvest():
    eventlog('hostname: ' + str(socket.gethostname()))
    websocket.enableTrace(True)

    harvest = WebHarvest('webharvest_instance_0')

    wst = threading.Thread(target=harvest.ws.run_forever)
    wst.daemon = True
    wst.start()

    initialized_server = False

    conn_timeout = 5
    while not harvest.ws.sock.connected and conn_timeout:
        sleep(1)
        conn_timeout -= 1

    msg_counter = 0
    try:
        while harvest.ws.sock.connected:
            sleep(5)
            if initialized_server == False:
                # if str(socket.gethostname()) != "tr3b" or str(socket.gethostname()) == "gman":
                harvest.set_all_users_to_inactive()
                harvest.subscribe_to_user_updates()
                initialized_server = True
            # harvest.get_update(harvest.ws)
    except:
        eventlog('disconnected....')
    
    harvest.alive = False
    sleep(1)
    wst.join()



if __name__ == "__main__":
    while True:
        try:
            run_webharvest()
        except Exception as e:
            eventlog("Exception: {}".format(e))
            eventlog('trying to connect...')
            sleep(5)

