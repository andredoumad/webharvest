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
        self.user_robot_assignment_dict = {}

    def on_message(self, ws, message):
        loaded_dict_data = json.loads(message)

        inactive_users_string = loaded_dict_data.get('inactive_users', None)
        active_users_string = loaded_dict_data.get('active_users', None)

        inactive_users_dict = json.loads(inactive_users_string)
        eventlog(str('TIME: ' + get_time_string()))
        for key, value in inactive_users_dict.items():
            eventlog(str('inactive_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))
            if self.user_robot_assignment_dict.get(str(key)) != None:
                self.remove_robot_from_user(str(key))


        active_users_dict = json.loads(active_users_string)

        for key, value in active_users_dict.items():
            eventlog(str('active_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))

            # if value == None:
            if self.user_robot_assignment_dict.get(str(key)) == None:
                eventlog(str('user: ' + str(key) + ' is active and needs a robot!'))
                self.assign_robot_to_user(str(key))

    def on_error(self, ws, error):
        print("on_error received error as {}".format(error))

    def on_close(self, ws):
        print("on_close Connection closed")

    def on_open(self, ws):
        sleep(3)

        text = {
            'robot_id': 'webharvest_robot_router',

        }
        ws.send(json.dumps(text))

    def on_data(self, ws):
        print("on_data received message as {}".format(message))

    def get_update(self, ws):
        text = {
            'robot_id': 'webharvest_robot_router',
        }
        ws.send(json.dumps(text))

    def assign_robot_to_user(self, human):
        eventlog('assign_robot_to_user....')
        thread = self.user_robot_assignment_dict.get(human)
        eventlog('thread: ' + str(thread))
        if thread == None:
            eventlog('human not found...')
            robot = ChatBot('Alice', str(human))
            chatbot_thread = threading.Thread(target=robot.run_chatbot)    
            chatbot_thread.daemon = True
            chatbot_thread.start()
            self.user_robot_assignment_dict[human] = robot
        
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
            # self.user_robot_assignment_dict[human] = ChatBot('Alice', str(human))

        # del self.user_robot_assignment_dict.get(human)
        robot = self.user_robot_assignment_dict.get(human)
        robot.alive = False
        # robot.join()
        # robot = self.user_robot_assignment_dict.get(human)
        # eventlog('robot removed: ' + str(robot))

        self.user_robot_assignment_dict[human] = None
        robot = self.user_robot_assignment_dict.get(human)
        eventlog('robot None: ' + str(robot))
        # robot.run_chatbot()

if __name__ == "__main__":
    eventlog('hostname: ' + str(socket.gethostname()))
    websocket.enableTrace(True)

    harvest = WebHarvest('webharvest_instance_0')

    wst = threading.Thread(target=harvest.ws.run_forever)
    wst.daemon = True
    wst.start()

    conn_timeout = 5
    while not harvest.ws.sock.connected and conn_timeout:
        sleep(1)
        conn_timeout -= 1

    msg_counter = 0
    while harvest.ws.sock.connected:
        sleep(5)
        harvest.get_update(harvest.ws)

        


















# VERSION 1










# # class webharvest:

# def on_message(ws, message):
#     '''
#         This method is invoked when ever the client
#         receives any message from server
#     '''
#     loaded_dict_data = json.loads(message)

#     inactive_users_string = loaded_dict_data.get('inactive_users', None)
#     active_users_string = loaded_dict_data.get('active_users', None)

#     inactive_users_dict = json.loads(inactive_users_string)
#     eventlog(str('TIME: ' + get_time_string()))
#     for key, value in inactive_users_dict.items():
#         eventlog(str('inactive_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))

#     active_users_dict = json.loads(active_users_string)

#     for key, value in active_users_dict.items():
#         eventlog(str('active_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))




# def on_error(ws, error):
#     '''
#         This method is invoked when there is an error in connectivity
#     '''
#     print("on_error received error as {}".format(error))

# def on_close(ws):
#     '''
#         This method is invoked when the connection between the 
#         client and server is closed
#     '''
#     print("on_close Connection closed")

# def on_open(ws):
#     '''
#         This method is invoked as soon as the connection between 
#         client and server is opened and only for the first time
#     '''

#     sleep(3)

#     text = {
#         'robot_id': 'webharvest_robot_router',

#     }
#     ws.send(json.dumps(text))


# def on_data(ws):
#     print("on_data received message as {}".format(message))


# def send_test_message(ws):
#     text = {
#         'robot_id': 'webharvest_robot_router',
#     }
#     ws.send(json.dumps(text))


# if __name__ == "__main__":
#     eventlog('hostname: ' + str(socket.gethostname()))
#     websocket.enableTrace(True)
#     if str(socket.gethostname()) == "tr3b":
#         ws = websocket.WebSocketApp(
#             "ws://127.0.0.1:8000/webharvest/",
#                                 on_message = on_message,
#                                 on_error = on_error,
#                                 on_close = on_close,
#                                 on_open = on_open)
#     else:
#         ws = websocket.WebSocketApp(
#             "wss://stringkeeper.com/webharvest/",
#                                 on_message = on_message,
#                                 on_error = on_error,
#                                 on_close = on_close,
#                                 on_open = on_open)

#     wst = threading.Thread(target=ws.run_forever)
#     wst.daemon = True
#     wst.start()

#     conn_timeout = 5
#     while not ws.sock.connected and conn_timeout:
#         sleep(1)
#         conn_timeout -= 1

#     msg_counter = 0
#     while ws.sock.connected:
#         sleep(15)
#         send_test_message(ws)
        










# VERSION 0









# import websocket
# from time import sleep
# import json
# from datetime import datetime
# import threading
# import socket
# import logging
# from standalone_tools import *

# def on_message(ws, message):
#     '''
#         This method is invoked when ever the client
#         receives any message from server
#     '''
#     loaded_dict_data = json.loads(message)

#     inactive_users_string = loaded_dict_data.get('inactive_users', None)
#     active_users_string = loaded_dict_data.get('active_users', None)

#     inactive_users_dict = json.loads(inactive_users_string)
#     eventlog(str('TIME: ' + get_time_string()))
#     for key, value in inactive_users_dict.items():
#         eventlog(str('inactive_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))

#     active_users_dict = json.loads(active_users_string)

#     for key, value in active_users_dict.items():
#         eventlog(str('active_user: ' + str(key) + ' assigned_robot_name: ' + str(value)))


# def on_error(ws, error):
#     '''
#         This method is invoked when there is an error in connectivity
#     '''
#     print("on_error received error as {}".format(error))

# def on_close(ws):
#     '''
#         This method is invoked when the connection between the 
#         client and server is closed
#     '''
#     print("on_close Connection closed")

# def on_open(ws):
#     '''
#         This method is invoked as soon as the connection between 
#         client and server is opened and only for the first time
#     '''
#     # ws.send("hello there")

#     sleep(3)
#     now = datetime.now()
#     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#     text = {
#         # 'message': str('alice on_open ' + str(dt_string)),
#         # 'username': 'Alice',
#         'robot_id': 'webharvest_robot_router',
#         # 'human': 'dante@stringkeeper.com'

#     }
#     ws.send(json.dumps(text))


# def on_data(ws):
#     print("on_data received message as {}".format(message))


# def send_test_message(ws):
#     now = datetime.now()
#     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#     text = str('Hello from Alice websocket ' + str(dt_string))
#     print(text)
#     text = {
#         # 'message': text,
#         # 'username': 'Alice',
#         'robot_id': 'webharvest_robot_router',
#         # 'human': 'dante@stringkeeper.com'
#     }
#     ws.send(json.dumps(text))


# if __name__ == "__main__":
#     eventlog('hostname: ' + str(socket.gethostname()))
#     websocket.enableTrace(True)
#     if str(socket.gethostname()) == "tr3b":
#         ws = websocket.WebSocketApp(
#             # "wss://stringkeeper.com/webharvest/",
#             "ws://127.0.0.1:8000/webharvest/",
#             # "ws://localhost:9090/ws",
#                                 on_message = on_message,
#                                 on_error = on_error,
#                                 on_close = on_close,
#                                 on_open = on_open)
#     else:
#         ws = websocket.WebSocketApp(
#             "wss://stringkeeper.com/webharvest/",
#             # "ws://127.0.0.1:8000/webharvest/",
#             # "ws://localhost:9090/ws",
#                                 on_message = on_message,
#                                 on_error = on_error,
#                                 on_close = on_close,
#                                 on_open = on_open)

#     # ws.on_open = on_open
#     # ws.run_forever()

#     wst = threading.Thread(target=ws.run_forever)
#     wst.daemon = True
#     wst.start()

#     conn_timeout = 5
#     while not ws.sock.connected and conn_timeout:
#         sleep(1)
#         conn_timeout -= 1

#     msg_counter = 0
#     while ws.sock.connected:
#         # print('Hello world %d'%msg_counter)
#         # ws.send('Hello world %d'%msg_counter)
#         # ws.on_data()


#         sleep(15)
#         send_test_message(ws)
        
#         # msg_counter += 1    

