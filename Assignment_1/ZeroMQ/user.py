import zmq
import json
import uuid
import datetime

USER_ID = str(uuid.uuid4())
SERVER_ADDRESS = "104.198.179.177"
SERVER_PORT = 4444

class User:
    def __init__(self):
        self.contextInstance = zmq.Context()
        self.socketInstance = self.contextInstance.socket(zmq.REQ)
        self.socketInstance.connect(f"tcp://{SERVER_ADDRESS}:{SERVER_PORT}")
        self.groupName = None
        self.groupPort = None
        self.groupIP = None

    def joinGroup(self):

        payload = {
            "method": "GetGroupList",
            "userID": USER_ID,
        }

        self.socketInstance.send(json.dumps(payload).encode("utf-8"))
        response = self.socketInstance.recv().decode("utf-8")
        groupList = json.loads(response)

        i = 1

        print("\nGroups:")

        for group in groupList:
            print(f"{i}. {group['groupName']} localhost:{group['port']}")
            i+=1
            
        print()

        index = int(input("Enter group number: ")) - 1

        if index < 0 or index >= len(groupList):
            print("Invalid group number")
            return
        print("Index", index)
        self.groupName = groupList[index]["groupName"]
        self.groupPort = groupList[index]["port"]
        self.groupIP = groupList[index]["IP"]
        self.groupSocket = self.contextInstance.socket(zmq.REQ)
        self.groupSocket.connect(f"tcp://{self.groupIP}:{self.groupPort}")
        response = self.groupSocket.send(
            json.dumps(
                {
                    "userID": USER_ID,
                    "method": "JoinGroup",
                }
            ).encode("utf-8")
        )
        response = self.groupSocket.recv().decode("utf-8")
        print()
        print(response)
    
    def leaveGroup(self):
        self.groupSocket.send(
            json.dumps(
                {
                    "userID": USER_ID,
                    "method": "LeaveGroup",
                }
            ).encode("utf-8")
        )
        response = self.groupSocket.recv().decode("utf-8")
        self.groupName = None
        self.groupPort = None
        self.groupIP = None
        print()
        print(response)
    
    def message(self):
        if not self.groupName:
            print("You are not in a group")
            return
        print()
        message = input("Enter message: ")
        name = input("Enter name: ")
        self.groupSocket.send(
            json.dumps(
                {
                    "userID": USER_ID,
                    "method": "SendMessage",
                    "params": {
                        "message": message,
                        "name": name,
                    }
                }
            ).encode("utf-8")
        )
        response = self.groupSocket.recv().decode("utf-8")
        print(response)
    
    def getMessages(self):
        if not self.groupName:
            print("You are not in a group")
            return
        print()
        date = input("Enter date (DD/MM/YYYY): ")
        self.groupSocket.send(
            json.dumps(
                {
                    "userID": USER_ID,
                    "method": "GetMessage",
                    "params": {
                        "date": date,
                    }
                }
            ).encode("utf-8")
        )
        response = self.groupSocket.recv().decode("utf-8")
        try:
            messageList = json.loads(response)
            for message in messageList:
                print(f"Sent By: {message['userName']}")
                print(f"Message: {message['message']}")
                print(f"Time: {datetime.datetime.fromtimestamp(message['timestamp']).strftime('%d/%m/%Y %H:%M:%S')}")
                print()
        except:
            print(response)
        
if __name__ == "__main__":
    user = User()
    while True:
        print()
        print("Select an option:")
        print("1. Join Group")
        print("2. Leave Group")
        print("3. Send Message")
        print("4. Get Messages")
        print("5. Exit")
        choice = int(input("Enter choice: "))

        if choice == 1:
            user.joinGroup()
        elif choice == 2:
            user.leaveGroup()
        elif choice == 3:
            user.message()
        elif choice == 4:
            user.getMessages()
        else:
            break