import map_reduce_pb2
import map_reduce_pb2_grpc
import time
import os
import json
from utils import get_distance, prob_gen


class MapperClass(map_reduce_pb2_grpc.MapperServiceServicer):
    def __init__(self, mapper_id, port, num_reducers):
        self.mapper_id = mapper_id
        self.indices = None
        self.centroids = None
        self.port = port
        self.num_reducers = num_reducers
        self.ip = "localhost"
        with open('config.json', 'r') as f:
            data = json.load(f)
        self.mappers = data["mappers"]
        self.reducers = data["reducers"]

    def pointsLoader(self, input_split):
        with open('./Input/points.txt') as f:
            lines = f.readlines()
        self.points = []
        for i in input_split:
            self.points.append(map_reduce_pb2.Point(x=float(lines[i].split(",")[0]), y=float(lines[i].split(",")[1])))
        return self.points

    def get_mapping(self,input_split,centroids):
        points = self.pointsLoader(input_split)
        groups = {}
        for point in points:
            min_distance = float('inf')
            for i in range(len(centroids)):
                centroid = centroids[i]
                distance = get_distance(point, centroid)
                if distance < min_distance:
                    min_distance = distance
                    group = i
            if group not in groups:
                groups[group] = []
            groups[group].append(point)

        # Here File Writing is missing
        # Here dump filing is missing(everywhere)
        self.groups = groups
        return groups


    def write_to_partition(self, output, mapper_id):
        directory = f'./Mappers/M{mapper_id}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        for reducer_id in self.reducers.keys():
            partitions = []
            partition_file = f'{directory}/partition_{reducer_id}.txt'
            for group in self.groups:
                if self.partition_function(group) == int(reducer_id):
                    for point in self.groups[group]:
                        partitions.append(map_reduce_pb2.MapOutput(centroid_id=group, point=point))
            with open(partition_file, 'w') as f:
                for partition in partitions:
                    f.write(f"{partition.centroid_id},{partition.point.x},{partition.point.y}\n")

    def Map(self,request,context):
        try:
            print(f"Mapper {self.mapper_id} request received from Master")
            input_split = request.input_split
            centroids = request.centroids
            flag = prob_gen()
            if not flag:
                print(f"Mapper {self.mapper_id} failed probability check")
                return map_reduce_pb2.MapResponse(mapper_id=self.mapper_id, status="FAILURE", map_output=[])
            groups = self.get_mapping(input_split, centroids)
            map_output = []
            for group in groups:
                for point in groups[group]:
                    map_output.append(map_reduce_pb2.MapOutput(centroid_id=group, point=point))
            time.sleep(10)
            self.write_to_partition(map_output, self.mapper_id)
            print(f"Mapper {self.mapper_id} request completed")
            return map_reduce_pb2.MapResponse(mapper_id=self.mapper_id, status="SUCCESS", map_output=map_output)
        except Exception as e:
            print(f"Mapper {self.mapper_id} failed",str(e))
            return map_reduce_pb2.MapResponse(mapper_id=self.mapper_id, status="FAILURE", map_output=[])
    
    def partition_function(self,centroid_id):
        return centroid_id % self.num_reducers + 1

    def GetIntermediateData(self,request,context):
        print(f"Mapper {self.mapper_id} request received from Reducer")
        try:
            reducer_id = request.reducer_id
            output = []
            for group in self.groups:
                if self.partition_function(group) == reducer_id:
                    for point in self.groups[group]:
                        output.append(map_reduce_pb2.MapOutput(centroid_id=group, point=point))

            print(f"Mapper {self.mapper_id} request completed")
            return map_reduce_pb2.IntermediateDataResponse(map_output=output,status="SUCCESS")
        except:
            return map_reduce_pb2.IntermediateDataResponse(map_output=[],status="FAILURE")
    
    