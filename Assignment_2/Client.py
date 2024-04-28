import grpc
import json
import sys
import random
import raft_pb2
import raft_pb2_grpc  
from threading import Thread
from pathlib import Path
import time

def runThread(func, args):
    myThread = Thread(target=func, args=args)
    myThread.daemon = True
    myThread.start()
    return myThread

def connectToNode(nodeID):
    with open("cluster.json", "r") as f:
      config = json.load(f)
    node_info = config[int(nodeID)-1]
    if not node_info:
      raise Exception(f"Node {nodeID} not found in configuration")
    nodeAddress = f"{node_info['ip']}:{node_info['port']}"
    return nodeAddress

def writeToFile(node, data):
    filename = f"node{node}/dump.txt"
    timestamp = time.strftime('%H:%M:%S', time.localtime(time.time()))
    data_with_timestamp = f"{timestamp} {data}"
    with open(filename, 'a') as f:
        f.write(data_with_timestamp + '\n')


class Client(raft_pb2_grpc.RaftService):
    def __init__(self, nodes):
        self.all_nodes = nodes
        self.leader = None

    def request_operation(self, key, value=None):
        if self.leader is None:
            print("No leader set. Trying random node")
            self.leader = random.choice(self.all_nodes)

        while True:
            operation_type = 'GET' if value is None else 'SET'
            print(f"Performing {operation_type} operation on key {key} on leader {self.leader}")
            address = connectToNode(self.leader)
            try:
                with grpc.insecure_channel(address) as channel:
                    stub = raft_pb2_grpc.RaftServiceStub(channel)
                    request = f"{operation_type} {key}" if value is None else f"{operation_type} {key} {value}"
                    response = stub.ServeClient(raft_pb2.ServeClientArgs(Request=request))
                    if not response.Success:
                        if response.LeaderID == "":
                            print("No established Leader.")
                            return None
                        if response.Data == "NOKEY" or response.Data == "NOCOMMIT":
                            print("Operation failed.")
                            return None
                        if response.LeaderID != "":
                            self.leader = response.LeaderID
                            print(f"Leader updated to {self.leader}.")
                    else:
                        print(response)
                        return response.Data
            except Exception as e:
                print("Node not found")
                self.leader = None
                return None

    def requestGET(self, key):
        return self.request_operation(key)

    def requestSET(self, key, value):
        return self.request_operation(key, value)



def load_cluster_configuration(filename):
    with open(filename, "r") as f:
        return json.load(f)

def parse_command(command):
    command_parts = command.split(' ')
    if len(command_parts) == 2 and command_parts[0] == 'GET':
        return 'GET', command_parts[1], None
    elif len(command_parts) == 3 and command_parts[0] == 'SET':
        return 'SET', command_parts[1], command_parts[2]
    else:
        return None, None, None

def process_command(client, command):
    command_type, key, value = parse_command(command)
    if command_type == 'GET':
        client.requestGET(key)
    elif command_type == 'SET':
        client.requestSET(key, value)
    else:
        print("Invalid command")

def main():
    try:
        config = load_cluster_configuration("cluster.json")
        nodes = [str(node['id']) for node in config]
        client = Client(nodes)
        
        while True:
            print("Enter 'GET key' or 'SET key value'")
            command = input()
            if command == 'exit':
                break
            process_command(client, command)
            
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)

if __name__ == '__main__':
    main()

