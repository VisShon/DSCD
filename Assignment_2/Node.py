import time
import threading
import sys
from concurrent import futures
import jsonpickle
from time import sleep
import tempfile
import os
import grpc 
import shutil
import grpc
import json
import sys
import random
import raft_pb2
import raft_pb2_grpc  

def runThread(func, args):
    myThread = threading.Thread(target=func, args=args)
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
        
class Node(raft_pb2_grpc.RaftService):    
    def __init__(self, id, cluster):
        self.currentTerm = -1
        self.votedFor = None
        self.log = []
        self.stateMachine = {}
        self.commitLength = 0
        self.currentRole = "FOLLOWER"
        self.currentLeader = None
        self.votesReceived = ()
        self.sentLength = {}
        self.ackedLength = {}
        self.nodeId = None
        self.ip = None
        self.port = None
        self.nodes = 0
        self.allNodes = None
        self.electionTimeout = 0
        self.heartbeatTimeout = 0
        self.leaseDuration = 5000
        self.waitTime = 0
        self.lease = {}
        self.heartbeats = {}
        self.myLeaderLease = 0
        self.initCluster(id, cluster)
        self.start_connection()
    
    def start_connection(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()
        client_thread = threading.Thread(target=self.initiate)
        client_thread.start()

        server_thread.join()
        client_thread.join()

    def run_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        raft_pb2_grpc.add_RaftServiceServicer_to_server(self, server)
        server.add_insecure_port('[::]:'+str(self.port))
        server.start()
        print("Server started at port: ", self.port)
        server.wait_for_termination()


    def initiate(self):
        self.recoveryFromCrash()
        self.setElectionTimer()
        self.startElectionTimer()
        self.setHeartbeatTimer()
        self.startHeartbeatTimer()

    def recoveryFromCrash(self):
        self.currentRole = "FOLLOWER"
        self.currentLeader = None
        self.votesReceived = ()
        self.sentLength = {}
        self.ackedLength = {}
        for node in self.allNodes:
            self.sentLength[node["id"]] = 0
            self.ackedLength[node["id"]] = 0
        self.loadFromMetadata()
    
    def loadFromMetadata(self):
        try:
            with open("node"+str(self.nodeId)+"/metadata.json", "r") as f:
                data = f.read()
                if data:
                    node = jsonpickle.decode(data)
                    self.currentTerm = node.currentTerm
                    self.votedFor = node.votedFor
                    self.log = node.log
                    self.commitLength = node.commitLength
                    self.currentRole = node.currentRole
                    self.currentLeader = node.currentLeader
                    self.votesReceived = node.votesReceived
                    self.sentLength = node.sentLength
                    self.ackedLength = node.ackedLength
                    self.electionTimeout = node.electionTimeout
                    self.heartbeatTimeout = node.heartbeatTimeout
                    self.waitTime = node.waitTime
                    self.myLeaderLease = node.myLeaderLease
                    self.leaseDuration = node.leaseDuration
                    self.stateMachine = node.stateMachine
                    self.setDictKeyAsNums()
                    
        except Exception as e:
            print("Error in loading from metadata.json")

    def setDictKeyAsNums(self):
        new_dict = {}
        for key in self.ackedLength:
            new_dict[int(key)] = self.ackedLength[key]
        self.ackedLength = new_dict

        new_dict = {}
        for key in self.sentLength:
            new_dict[int(key)] = self.sentLength[key]
        self.sentLength = new_dict

        new_dict = {}
        for key in self.lease:
            new_dict[int(key)] = self.lease[key]
        self.lease = new_dict

        new_dict = {}
        for key in self.heartbeats:
            new_dict[int(key)] = self.heartbeats[key]
        self.heartbeats = new_dict
        
    def initCluster(self, id, cluster):
        self.nodeId = id
        self.ip = cluster[id-1]["ip"]
        self.port = cluster[id-1]["port"]
        self.nodes = len(cluster)
        self.allNodes = cluster
        for node in cluster:
            self.sentLength[node["id"]] = 0
            self.ackedLength[node["id"]] = 0
            self.heartbeats[node["id"]] = False

    
    def startElection(self):
        print("Starting Election")
        self.currentTerm += 1
        print("Current Term: ", self.currentTerm)
        self.currentRole = "CANDIDATE"
        self.votedFor = self.nodeId
        writeToFile(self.nodeId,f"Vote granted for Node {self.nodeId} in term {self.currentTerm}.")
        self.votesReceived ={self.nodeId}
        self.LastTerm = 0
        if len(self.log) > 0:
            self.LastTerm = self.log[-1]["Term"]
        request = raft_pb2.VoteRequest(term = self.currentTerm, candidateId=self.nodeId, lastLogIndex=len(self.log), lastLogTerm=self.LastTerm)
        threads = []
        for node in self.allNodes:
            if node["id"] != self.nodeId:
                t = runThread(self.requestVote, (node["id"], request))
                threads.append(t)
        for t in threads:
            t.join()

    def requestVote(self, nodeId, request):
        try:
            address = connectToNode(nodeId)
            with grpc.insecure_channel(address) as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                response = stub.VoteRequested(request)
                self.receivedVoteReply(response)
        except Exception as e:
            print(f"Error in Requesting Vote to Node ID: {nodeId}")
            writeToFile(self.nodeId, f"Error occurred while sending RPC to Node {nodeId}.")

    def receivedVoteReply(self, response):
        voterId = response.nodeId
        term = response.term
        granted = response.voteGranted
        voterleaderLease = response.leaderLease
        self.lease[voterId] = voterleaderLease 
        
        if self.currentRole == "CANDIDATE" and term == self.currentTerm and granted:
            self.votesReceived.add(voterId)
            self.heartbeats[voterId] = True
            self.waitTime = max(self.waitTime, voterleaderLease)
            if len(self.votesReceived) >= self.nodes//2+1:
                print("MAJORITY Votes Received")
                self.setElectionTimer()
                writeToFile(self.nodeId,f"Node {self.nodeId} became the leader for term {self.currentTerm}")
                writeToFile(self.nodeId,"Leader waiting for Old Leader Lease to timeout.")
                print("Waittime:", self.waitTime, time.time())
                if self.waitTime > time.time():
                    sleep(self.waitTime - time.time())

                self.currentRole = "LEADER"
                self.currentLeader = self.nodeId

                self.log.append({"op": "NO-OP", "key": "", "value": "", "Term": self.currentTerm})
               
                threads = []
                for follower in self.allNodes:
                    if follower['id'] != self.nodeId:
                        self.sentLength[follower['id']] = len(self.log)
                        self.ackedLength[follower['id']] = 0
                        t = runThread(self.replicateLog, (follower['id'],))
                        threads.append(t)

        elif term > self.currentTerm:
            self.currentTerm = term
            self.currentRole = "FOLLOWER"
            self.votedFor = None
            writeToFile(self.nodeId,f"{self.nodeId} Stepping down")
            self.setElectionTimer()
    
    def setElectionTimer(self):
        self.electionTimeout = time.time() + random.randint(5000, 10000) / 1000

    def startElectionTimer(self):
        runThread(self.checkElectionTimeout, ())
    
    def checkElectionTimeout(self):
        while True:
            if time.time() > self.electionTimeout and (self.currentRole == 'FOLLOWER' or self.currentRole == 'CANDIDATE'):
                print("Timeout Occurred!")
                writeToFile(self.nodeId,f"Node {self.nodeId} election timer timed out, Starting election.")
                self.setElectionTimer()
                self.currentLeader = None
                self.startElection()
                

    def setHeartbeatTimer(self):
        self.heartbeatTimeout = time.time() + 1000 / 1000
    
    def startHeartbeatTimer(self):
        runThread(self.checkHeartbeatTimeout, ())
    
    def resetHeartbeats(self):
        for key in self.heartbeats:
            self.heartbeats[key] = False

    def checkHeartbeatTimeout(self):
        while True:
            if time.time() > self.heartbeatTimeout:
                self.saveToMetadata()
            if time.time() > self.heartbeatTimeout and self.currentRole == 'LEADER':
                print("Heartbeat Timeout Occurred!")
                writeToFile(self.nodeId, f"Leader {self.nodeId} sending heartbeat & Renewing Lease")
                self.setHeartbeatTimer()
                self.broadcast()
                count = 1
                currentTime = time.time()
                print("currentTime:", currentTime)
                print("checking leader lease:", self.heartbeats)
                for key in self.heartbeats:
                    if key != self.nodeId and self.heartbeats[key]:
                        count += 1
                if count >= self.nodes//2 + 1:
                    print(count)
                    print("Leader Still Leader")
                    self.myLeaderLease = time.time() + self.leaseDuration/1000
                    
                if time.time() > self.myLeaderLease:
                    print("Leader Lease Timeout")
                    self.currentTerm = self.currentTerm
                    self.currentRole = "FOLLOWER"
                    writeToFile(self.nodeId,f"Leader {self.nodeId} lease renewal failed. Stepping Down.")
                    self.votedFor = None
                    writeToFile(self.nodeId,f"{self.nodeId} Stepping down")
                    self.myLeaderLease = time.time() + self.leaseDuration/1000
                    self.setElectionTimer()
    
    def getLeaderLease(self):
        return self.myLeaderLease

    def VoteRequested(self, request, context):
        cId = request.candidateId
        cTerm = request.term
        cLogLength = request.lastLogIndex
        cLogTerm = request.lastLogTerm

        if cTerm > self.currentTerm:
            self.currentTerm = cTerm
            self.currentRole = "FOLLOWER"
            self.votedFor = None
            self.setElectionTimer()
        
        self.LastTerm = 0
        if len(self.log) > 0:
            self.LastTerm = self.log[-1]["Term"]
        logOk = (cLogTerm > self.LastTerm) or (cLogTerm == self.LastTerm and cLogLength >= len(self.log))
        if cTerm == self.currentTerm and (self.votedFor == None or self.votedFor == cId) and logOk:
            self.votedFor = cId
            self.setElectionTimer()
            writeToFile(self.nodeId,f"Vote granted for Node {cId} in term {cTerm}.")
            return raft_pb2.VoteResponse(nodeId= self.nodeId, term=self.currentTerm, voteGranted=True, leaderLease=self.getLeaderLease())
        else:
            writeToFile(self.nodeId,f"Vote denied for Node {cId} in term {cTerm}.")
            return raft_pb2.VoteResponse(nodeId= self.nodeId, term=self.currentTerm, voteGranted=False, leaderLease=self.getLeaderLease())

    def replicateLog(self, followerId):
        prefixLen = self.sentLength[followerId]
        suffix = []
        for i in range(prefixLen, len(self.log)):
            suffix.append(raft_pb2.SuffixEntry(op = self.log[i]["op"], term=self.log[i]["Term"], key=self.log[i]["key"], value = self.log[i]["value"]))
        prefixTerm = 0
        if prefixLen > 0:
            prefixTerm = self.log[prefixLen - 1]["Term"]
        request = raft_pb2.LogRequest(leaderId=self.nodeId, currentTerm=self.currentTerm, prefixLen=prefixLen, prefixTerm=prefixTerm, commitLength=self.commitLength, suffix=suffix, leaderLease=self.myLeaderLease)
        try:
            address = connectToNode(followerId)
            with grpc.insecure_channel(address) as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                response = stub.LoggingRequested(request)
                self.receivedLogReply(response)
        except Exception as e:
            print(f"Error in Replicating Log to Node ID: {followerId}")
            writeToFile(self.nodeId, f"Error occurred while sending RPC to Node {followerId}.")
        
    def LoggingRequested(self, request, context):
        leaderId = request.leaderId
        term = request.currentTerm
        prefixLen = request.prefixLen
        prefixTerm = request.prefixTerm
        commitLength = request.commitLength
        suffix = request.suffix
        self.myLeaderLease = request.leaderLease

        self.setElectionTimer()
        if term > self.currentTerm:
            self.currentTerm = term
            self.votedFor = None
            self.setElectionTimer()

        if term == self.currentTerm:
            self.currentRole = "FOLLOWER"
            self.currentLeader = leaderId
        logOk = (len(self.log) >= prefixLen) and (prefixLen == 0 or prefixTerm == self.log[prefixLen - 1]["Term"])
        print("Log: ", self.log)
        print(len(self.log))
        print("Log OK: ", logOk)
        print("Prefix Length: ", prefixLen)
        print("Suffix: ", suffix)
        print("prefixTerm: ", prefixTerm)
        try:
            print(self.log[prefixLen - 1]["Term"])
        except:
            print("WHAT")

        try:
            if term == self.currentTerm and logOk:
                self.appendEntries(prefixLen, commitLength, suffix, leaderId)
                ack = prefixLen + len(suffix)
                return raft_pb2.LogResponse(nodeId=self.nodeId, term=self.currentTerm, ack=ack, success=True)
            else:
                writeToFile(self.nodeId,f"Node {self.nodeId} rejected AppendEntries RPC from {leaderId}.")
                return raft_pb2.LogResponse(nodeId=self.nodeId, term=self.currentTerm, ack=0, success=False)
        except Exception as e:
            print(f"Error in Logging Request from Node ID: {leaderId}")


    def appendEntries(self, prefixLen, leaderCommit, suffix, leaderId):
        if len(suffix) > 0 and len(self.log) > prefixLen:
            index = min(len(self.log), prefixLen + len(suffix)) -1
            print("Index: ", index, len(self.log), prefixLen, len(suffix))
            print("WOAH",self.log[index]["Term"])
            if self.log[index]["Term"] != suffix[index - prefixLen].term:
                print("check1: ", index, len(suffix))
                self.log = self.log[:prefixLen]
        if prefixLen + len(suffix) > len(self.log):
            for i in range(len(self.log) - prefixLen, len(suffix)):
                print("check2: ", i, len(suffix))
                self.log.append({"op": suffix[i].op, "key": suffix[i].key,"value":suffix[i].value ,"Term": suffix[i].term})
                '''CHECKKK'''
            writeToFile(self.nodeId,f"Node {self.nodeId} accepted AppendEntries RPC from {leaderId}.")

        if leaderCommit > self.commitLength:
            for i in range(self.commitLength, leaderCommit):
                self.stateMachine[self.log[i]["key"]] = self.log[i]["value"]
                entry = " ".join(map(str, self.log[i].values()))                
                writeToFile(self.nodeId,f"Node {self.nodeId} (follower) committed the entry {entry} to the state machine.")
            self.commitLength = leaderCommit


    def receivedLogReply(self, response):
        term = response.term
        ack = response.ack
        success = response.success
        follower = response.nodeId
        self.heartbeats[follower] = success
        if term == self.currentTerm and self.currentRole == "LEADER":
            if success and ack >= self.ackedLength[follower]:
                self.sentLength[follower] = ack
                self.ackedLength[follower] = ack
                self.commitLogEntries()
            elif self.sentLength[follower] > 0:
                print("Replicating Log to: ", follower)
                self.sentLength[follower] -= 1
                self.replicateLog(follower)
        elif term > self.currentTerm:
            self.currentTerm = term
            self.currentRole = "FOLLOWER"
            self.votedFor = None
            writeToFile(self.nodeId,f"{self.nodeId} Stepping down")
            self.setElectionTimer()


    def acks(self,length):
        count = 0
        for i in range(1,len(self.ackedLength)+1):
            if self.ackedLength[i] >= length:
                count += 1
            else:
                print("ACK: ", self.ackedLength[i])
                print("Length: ", length)
        return count
    
    def commitLogEntries(self):
        minacks = self.nodes//2 + 1
        ready = []
        for i in range(1,len(self.log)+1):
            print("length: ", i)
            print("ackedLength: ", self.ackedLength)
            if self.acks(i) >= minacks:
                ready.append(i)
            else:
                print("self.acks(i)",self.acks(i))
        
        maxval = max(ready)
        print("maxval",maxval)
        print("ready",ready)
        if len(ready) > 0 and maxval > self.commitLength and self.log[maxval-1]["Term"] == self.currentTerm:
            print("Committing Log Entries")
            for i in range(self.commitLength, maxval):
                self.stateMachine[self.log[i]["key"]] = self.log[i]["value"]
                print("State Machine: ", self.stateMachine)
                entry = " ".join(map(str, self.log[i].values()))                
                writeToFile(self.nodeId,f"Node {self.nodeId} (leader) committed the entry {entry} to the state machine.")
            self.commitLength = maxval

    def ServeClient(self, request, context):
        print("Client Request")
        if self.currentRole == "LEADER":
            message = request.Request
            writeToFile(self.nodeId,f"Node {self.nodeId} (leader) received an {message} request.")
            if message.split()[0] == "GET":
                key = message.split()[1]
                if key in self.stateMachine:
                    return raft_pb2.ServeClientReply(Data=self.stateMachine[key], LeaderID=str(self.currentLeader), Success=True)
                else: 
                    return raft_pb2.ServeClientReply(Data="NOKEY", LeaderID=str(self.currentLeader), Success=False)
            elif message.split()[0] == "SET": 
                key = message.split()[1]
                value = message.split()[2]     
                self.log.append({"op": "SET", "key": key, "value":value,"Term": self.currentTerm})
                self.ackedLength[self.nodeId] = len(self.log)
                currentCommit = self.commitLength
                threads = []
                for follower in self.allNodes:
                        if follower['id'] != self.nodeId:
                            t = runThread(self.replicateLog, (follower['id'],))
                            threads.append(t)
                for t in threads:
                    t.join()
                if currentCommit >= self.commitLength:
                    return raft_pb2.ServeClientReply(Data="NOCOMMIT", LeaderID=str(self.currentLeader), Success=False)
                else:
                    return raft_pb2.ServeClientReply(Data="", LeaderID=str(self.currentLeader), Success=True)
        else:
            if self.currentLeader:
                return raft_pb2.ServeClientReply(Data="", LeaderID=str(self.currentLeader), Success=False)
            else:
                return raft_pb2.ServeClientReply(Data="", LeaderID="", Success=False)

    def saveToMetadata(self):
        file_name = "node"+str(self.nodeId)+"/metadata"+".json"
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            data = json.loads(jsonpickle.encode(self))
            json.dump(data, f, indent=4)
            tempname = f.name
        shutil.move(tempname, file_name)

        file_name = "node"+str(self.nodeId)+"/logs.txt"
        log_text = ""
        for log in self.log:
            log_text += ' '.join(map(str, log.values()))
            log_text += "\n"

        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            f.write(log_text)
            tempname = f.name
        shutil.move(tempname, file_name)
    


    def broadcast(self):
        print("LEADER: ", self.currentLeader, "Broadcasting")
        if self.currentRole == "LEADER":
            threads = []
            for follower in self.allNodes:
                self.ackedLength[self.nodeId] = len(self.log)
                if follower['id'] != self.nodeId:
                    self.heartbeats[follower['id']] = False
                    t = runThread(self.replicateLog, (follower['id'],))
                    threads.append(t)
            for t in threads:
                t.join()

if __name__ == '__main__':
    with open('cluster.json') as f:
        data = json.load(f)
    cluster = data
    for node in cluster:
        node["id"] = int(node["id"])

    if len(sys.argv) < 2:
        print("Please provide the id for this node")
        sys.exit()

    node_id = int(sys.argv[1])
    dir_name = "node"+str(node_id)
    
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    node = Node(node_id, cluster)
