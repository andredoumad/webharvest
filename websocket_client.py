import websocket
from time import sleep
import json
from datetime import datetime
import threading

# class websocket_client:

# def __init__(self, name):
#     self.name = name
#     # self.api_url = 'https://stringkeeper.com/webhooks/webharvest/'
#     self.api_url = 'http://127.0.0.1:8000/webhooks/webharvest/'
#     self.user = ''
#     self.chat = ''
#     self.response = None

def on_message(ws, message):
    '''
        This method is invoked when ever the client
        receives any message from server
    '''
    print("on_message received message as {}".format(message))
    # ws.send("hello again")
    # print("sending 'hello again'")

def on_error(ws, error):
    '''
        This method is invoked when there is an error in connectivity
    '''
    print("on_error received error as {}".format(error))

def on_close(ws):
    '''
        This method is invoked when the connection between the 
        client and server is closed
    '''
    print("on_close Connection closed")

def on_open(ws):
    '''
        This method is invoked as soon as the connection between 
        client and server is opened and only for the first time
    '''
    # ws.send("hello there")

    sleep(3)
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    text = {
        'message': str('alice on_open ' + str(dt_string)),
        'username': 'Alice',
        'robot_id': 'Alice_0'

    }
    ws.send(json.dumps(text))


def on_data(ws):
    print("on_data received message as {}".format(message))


def send_test_message(ws):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    text = str('Hello from Alice websocket ' + str(dt_string))
    print(text)
    text = {
        'message': text,
        'username': 'Alice',
        'robot_id': 'Alice_0'
    }
    ws.send(json.dumps(text))


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        # "wss://stringkeeper.com/webharvest/",
        "ws://127.0.0.1:8000/webharvest/",
        # "ws://localhost:9090/ws",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open)
    # ws.on_open = on_open
    # ws.run_forever()

    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

    conn_timeout = 5
    while not ws.sock.connected and conn_timeout:
        sleep(1)
        conn_timeout -= 1

    msg_counter = 0
    while ws.sock.connected:
        # print('Hello world %d'%msg_counter)
        # ws.send('Hello world %d'%msg_counter)
        # ws.on_data()


        sleep(10)
        send_test_message(ws)
        
        # msg_counter += 1    