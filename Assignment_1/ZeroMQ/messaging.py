import zmq
import json

SERVER_PORT = 4444
MAXIMUM_GROUPS = 10

groupList = []

contextInstance = zmq.Context()
socketInstance = contextInstance.socket(zmq.REP)
socketInstance.bind(f"tcp://*:{SERVER_PORT}")

print(f"Message Server listening on localhost:{SERVER_PORT}")

while True:
    payload = socketInstance.recv()
    payload = payload.decode("utf-8")
    payload = json.loads(payload)
    client = None
    if "userID" in payload:
        client = payload["userID"]
    elif "groupName" in payload:
        client = payload["groupName"]

    if payload["method"] == "MessageServer":
        if len(groupList) == MAXIMUM_GROUPS:
            print(f"MAX_GROUPS reached, rejecting group {payload['groupID']}")
            socketInstance.send(b"FAILURE")
            continue
        if payload["groupName"] in groupList:
            print(f"Group {payload['groupName']} already registered")
            socketInstance.send(b"SUCCESS")
            continue
        print(
            f"JOIN REQUEST FROM [IP: {payload['params']['IP']}, PORT: {payload['params']['port']}]"
        )
        groupList.append(
            {"groupName": payload["groupName"], "port": payload["params"]["port"], "IP": payload["params"]["IP"]}
        )
        socketInstance.send(b"SUCCESS")

    elif payload["method"] == "GetGroupList":
        print(f"GROUP LIST REQUEST FROM {payload['userID']}")
        socketInstance.send(json.dumps(groupList, default=tuple).encode("utf-8"))

    else:
        socketInstance.send(b"INVALID REQUEST")
