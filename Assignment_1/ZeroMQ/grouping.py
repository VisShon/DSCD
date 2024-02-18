import zmq
import uuid
import socket
import time
from datetime import datetime
import json

SERVER_ADDRESS = "104.198.179.177"
SERVER_PORT = 4444
MAXIMUM_USERS = 3


def getIP():
    socketInstance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socketInstance.connect(('10.255.255.255', 1))
        IP = socketInstance.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        socketInstance.close()
    return IP

IP = getIP()

contextInstance = zmq.Context()
socketInstance = contextInstance.socket(zmq.REQ)
groupName = input("Enter the name of the group: ")
portNumber = input("Enter port number: ")

payload = {
    "method": "MessageServer",
    "params": {"port": portNumber, "IP": IP},
    "groupName": groupName,
}

socketInstance.connect(f"tcp://{SERVER_ADDRESS}:{SERVER_PORT}")

print("Registering Group on Message Server")
socketInstance.send(json.dumps(payload).encode("utf-8"))
response = socketInstance.recv().decode("utf-8")
print(f"Response: {response}")
if response != "SUCCESS":
    exit()

socketInstance = contextInstance.socket(zmq.REP)
socketInstance.bind(f"tcp://*:{portNumber}")
print(f"[x] Server {groupName} listening on localhost:{portNumber}")

messageQueue = []
USERTELE = set()

while True:
    payload = socketInstance.recv()
    payload = payload.decode("utf-8")
    payload = json.loads(payload)

    method = payload["method"]
    userID = payload["userID"]
    params = payload["params"] if "params" in payload else {}

    print(f"[.] {method} request from {userID}")

    if method == "JoinGroup":
        if len(USERTELE) == MAXIMUM_USERS:
            print("[.] MAX_USERS reached, rejecting client %r", userID)
            socketInstance.send(b"FAIL")
        elif userID in USERTELE:
            print(f"Client {userID} is already in group")
            socketInstance.send(b"SUCCESS")
            continue
        else:
            print(f"JOIN REQUEST FROM {userID}")
            USERTELE.add(userID)
            socketInstance.send(b"SUCCESS")

    elif method == "LeaveGroup":
        if userID not in USERTELE:
            print(f"Client {userID} is not in group")
            socketInstance.send(b"FAIL")
        else:
            print(f"LEAVE REQUEST FROM {userID}")
            USERTELE.remove(userID)
            socketInstance.send(b"SUCCESS")

    elif method == "SendMessage":
        if userID not in USERTELE:
            socketInstance.send(b"FAIL")
        else:
            print(f" MESSAGE SEND FROM {userID}")
            message = {
                "userName": params["name"],
                "userID": userID,
                "message": params["message"],
                "timestamp": time.time(),
            }
            messageQueue.append(message)
            socketInstance.send(b"SUCCESS")

    elif method == "GetMessage":
        if userID not in USERTELE:
            socketInstance.send(b"FAIL")
        else:
            date = params["date"]
            if date == '':
                date = '01/10/2020'
            timestamp = time.mktime(datetime.strptime(date, "%d/%m/%Y").timetuple())
            
            print(f"MESSAGE REQUEST FROM {userID}")
            result = [x for x in messageQueue if x["timestamp"] >= timestamp]
            socketInstance.send(json.dumps(list(result)).encode("utf-8"))

    else:
        socketInstance.send(b"INVALID REQUEST")