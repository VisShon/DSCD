import grpc
import map_reduce_pb2
import map_reduce_pb2_grpc
from subprocess import Popen
import random
import time
import threading
import json


class Master(map_reduce_pb2_grpc.MasterServiceServicer):
    def __init__(self,num_mappers,num_reducers,num_centroids,max_iterations):
        self.num_mappers = num_mappers
        self.num_reducers = num_reducers
        self.num_centroids = num_centroids
        self.max_iterations = max_iterations
        self.centroids = []
        self.port = 50051
        self.ip = 'localhost'
        random.seed(231101)
        data = {}
        data["master"] = {
            "ip": self.ip,
            "port": self.port
        }
        processes = []
        data["mappers"] = {}
        for i in range(self.num_mappers):
            data["mappers"][str(i+1)] = {
                    "ip": "localhost",
                    "port": 50051 + i + 1
            }
            t = threading.Thread(target=self.start_mapper,args=(i+1,50051+i+1))
            t.start()
            processes.append(t)

        data["reducers"] = {}
        for i in range(self.num_reducers):
            data["reducers"][str(i+1)] = {
                    "ip": "localhost",
                    "port": 50051 + i + 1 + self.num_mappers
            }
            t = threading.Thread(target=self.start_reducer,args=(i+1,50051+i+1+self.num_mappers))
            t.start()
            processes.append(t)
        with open('config.json', 'w') as f:
            json.dump(data, f)
        self.data = data
        print("Waiting for process to join")
        for process in processes:
            process.join()
        print("All processes joined")
        self.input_split()

    def input_split(self):
        dumpfile = open('dump.txt','w').close()
        print("Starting input split")
        with open('./Input/points.txt') as f:
            lines = f.readlines()
        points = [map_reduce_pb2.Point(x=float(point.split(",")[0]), y=float(point.split(",")[1])) for point in lines]
        self.centroids = random.sample(points, self.num_centroids)
        mapper_indices = {}
        for i in range(len(points)):
            mapper_id = i % self.num_mappers + 1
            if mapper_id not in mapper_indices:
                mapper_indices[mapper_id] = []
            mapper_indices[mapper_id].append(i)
        self.mapper_indices = mapper_indices

    def start_mapper(self,mapper_id,port):
        Popen(["python", "initMapper.py", "--mapper_id", f"{mapper_id}", "--port", f"{port}", "--num_reducers", f'{self.num_reducers}'])
        time.sleep(3)

    def mapper(self,stub,i):
        try:
            dumpfile = open('dump.txt','a')
            dumpfile.write(f"grpc call Map from Mapper {i}\n")
            dumpfile.close()
            response = stub.Map(map_reduce_pb2.MapRequest(centroids=self.centroids, input_split=self.mapper_indices[i]))
            if response.status == "SUCCESS":
                dumpfile = open('dump.txt','a')
                dumpfile.write(f"grpc call Map from Mapper {i} returned SUCCESS\n")
                dumpfile.close()
                self.successfull_mapper[i] = True
            else:
                dumpfile = open('dump.txt','a')
                dumpfile.write(f"grpc call Map from Mapper {i} returned FAILURE\n")
                dumpfile.close()
                return False
        except:
            print(f"Mapper {i} connection failed")
            dumpfile = open('dump.txt','a')
            dumpfile.write(f"Mapper {i} connection failed\n")
            dumpfile.close()
            time.sleep(3)
            Popen(["python", "initMapper.py", "--mapper_id", f"{i}", "--port", f"{50051+i}", "--num_reducers", f'{self.num_reducers}'])

    def mapping(self):
        print("Starting Mapping")
        self.successfull_mapper = {}
        for i in range(1,self.num_mappers+1):
                self.successfull_mapper[i] = False
        while True:
            processes = []
            for i in range(1,self.num_mappers+1):
                if self.successfull_mapper.get(i,False):
                    continue
                print(f"Mapping {i}")
                try:
                    mapper_port = self.data["mappers"][str(i)]["port"]
                    mapper_ip = self.data["mappers"][str(i)]["ip"]
                    channel = grpc.insecure_channel(f'{mapper_ip}:{mapper_port}')
                    stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
                    t = threading.Thread(target=self.mapper,args=(stub,i))
                    t.start()
                except:
                    print(f"Mapper {i} connection failed")

                processes.append(t)
             
            for process in processes:
                process.join()
            if all(self.successfull_mapper.values()):
                break
            time.sleep(3)

    def start_reducer(self,reducer_id,port):
        Popen(["python", "initReducer.py", "--reducer_id", f"{reducer_id}", "--port", f"{port}", "--num_mappers", f"{self.num_mappers}"])
        time.sleep(3)

    def reduce(self,stub,i):
        try:
            dumpfile = open('dump.txt','a')
            dumpfile.write(f"grpc call Reduce from Reducer {i}\n")
            dumpfile.close()
            response = stub.Reduce(map_reduce_pb2.ReduceRequest())
            if response.status == "SUCCESS":
                dumpfile = open('dump.txt','a')
                dumpfile.write(f"grpc call Reduce from Reducer {i} returned SUCCESS\n")
                dumpfile.write(f"New Centroids from Reducer {i}:\n")
                for centroid in response.new_centroids:
                    dumpfile.write(f"Centroid {centroid.centroid_id} : x = {centroid.point.x}, y = {centroid.point.y}\n")
                dumpfile.close()
                self.successfull_reducer[i] = True
                for centroid in response.new_centroids:
                    self.new_centroids[centroid.centroid_id] = centroid.point
            else:
                dumpfile = open('dump.txt','a')
                dumpfile.write(f"grpc call Reduce from Reducer {i} returned FAILURE\n")
                dumpfile.close()
                return False
        except:
            print(f"Reducer {i} connection failed")
            dumpfile = open('dump.txt','a')
            dumpfile.write(f"Reducer {i} connection failed\n")
            dumpfile.close()
            time.sleep(3)
            Popen(["python", "initReducer.py", "--reducer_id", f"{i}", "--port", f"{50051+i+self.num_mappers}", "--num_mappers", f"{self.num_mappers}"])

    def reducing(self):
        print("Starting Reducing")
        self.successfull_reducer = {}
        for i in range(1,self.num_reducers+1):
            self.successfull_reducer[i] = False
        while True:
            processes = []
            for i in range(1,self.num_reducers+1):
                if self.successfull_reducer.get(i,False):
                    continue
                print(f"Reducing {i}")
                try:
                    reducer_port = self.data["reducers"][str(i)]["port"]
                    reducer_ip = self.data["reducers"][str(i)]["ip"]
                    channel = grpc.insecure_channel(f'{reducer_ip}:{reducer_port}')
                    stub = map_reduce_pb2_grpc.ReducerServiceStub(channel)
                    t = threading.Thread(target=self.reduce,args=(stub,i))
                    t.start()
                    processes.append(t)
                except:
                    print(f"Reducer {i} connection failed")

            for process in processes:
                process.join()
            if all(self.successfull_reducer.values()):
                break
            time.sleep(3)


    def run(self):
        for i in range(self.max_iterations):
            print(f"Iteration {i+1}")
            dumpfile = open('dump.txt','a')
            dumpfile.write("\n")
            dumpfile.write(f"Iteration {i+1}\n")
            dumpfile.close()
            if i == 0:
                dumpfile = open('dump.txt','a')
                dumpfile.write("Initial Centroids:\n")
                for j in range(len(self.centroids)):
                    dumpfile.write(f"Initial Centroid {j+1} : x = {self.centroids[j].x}, y = {self.centroids[j].y}\n")
                dumpfile.close()
            self.mapping()
            self.new_centroids = {}
            self.reducing()
            if all([self.centroids[i] == self.new_centroids[i] for i in range(self.num_centroids)]):
                print("Converged at iteration: ",i+1)
                dumpfile = open('dump.txt','a')
                dumpfile.write(f"Converged at iteration: {i+1}\n")
                dumpfile.close()
                break
            self.centroids = [self.new_centroids[i] for i in range(self.num_centroids)]
        for j in range(len(self.centroids)):
            dumpfile = open('dump.txt','a')
            dumpfile.write(f"Final Centroid {j+1} : x = {self.centroids[j].x}, y = {self.centroids[j].y}\n")
            dumpfile.close()
            print(f"Centroid {j+1} : x = {self.centroids[j].x}, y = {self.centroids[j].y}")