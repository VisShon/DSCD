import grpc
import map_reduce_pb2
import map_reduce_pb2_grpc
import time
import json
from utils import prob_gen, shuffle_and_sort, get_new_centroids


class ReducerClass(map_reduce_pb2_grpc.ReducerServiceServicer):
    def __init__(self, reducer_id, port, num_mappers):
        self.reducer_id = reducer_id
        self.indices = None
        self.centroids = None
        self.port = port
        self.num_mappers = num_mappers
        self.ip = "localhost"
        with open('config.json', 'r') as f:
            data = json.load(f)
        self.mappers = data["mappers"]
        self.reducers = data["reducers"]

    def get_data(self):
        data = []
        for i in range(1,int(self.num_mappers)+1):
            mapper_port = self.mappers[str(i)]["port"]
            mapper_ip = self.mappers[str(i)]["ip"]
            channel = grpc.insecure_channel(f'{mapper_ip}:{mapper_port}')
            stub = map_reduce_pb2_grpc.MapperServiceStub(channel)
            request = map_reduce_pb2.IntermediateDataRequest(reducer_id=self.reducer_id)
            dumpfile = f"./Reducers/dumpR{self.reducer_id}.txt"
            with open(dumpfile, 'a') as f:
                f.write(f"grpc request GetIntermediateData to Mapper {i} for data\n")
            response = stub.GetIntermediateData(request)
            if response.status == "SUCCESS":
                dumpfile = f"./Reducers/dumpR{self.reducer_id}.txt"
                with open(dumpfile, 'a') as f:
                    f.write(f"grpc call GetIntermediateData from Mapper {i} returned SUCCESS\n")
                    f.write(f"Received data from Mapper {i}\n")
                    for d in response.map_output:
                        f.write(f"{d.centroid_id},{d.point.x},{d.point.y}\n")
                data += response.map_output
            else:
                dumpfile = f"./Reducers/dumpR{self.reducer_id}.txt"
                with open(dumpfile, 'a') as f:
                    f.write(f"grpc call GetIntermediateData from Mapper {i} returned FAILURE\n")
                raise Exception("Error in getting intermediate data")
        return data
        
    def write_result(self, new_centroids):
        directory = f'./Reducers'

        with open(f"{directory}/R{self.reducer_id}.txt", 'w') as f:
            for key in new_centroids:
                f.write(f"{key},{new_centroids[key].x},{new_centroids[key].y}\n")
    
    def Reduce(self, request, context):
        print(f"Reducer {self.reducer_id} request received from Master")
        flag = prob_gen()
        try:
            if not flag:
                print(f"Reducer {self.reducer_id} failed probability check")
                return map_reduce_pb2.ReduceResponse(reducer_id=self.reducer_id, status="FAILURE")

            data = self.get_data()
            grouped_data = shuffle_and_sort(data)
            new_centroids = get_new_centroids(grouped_data)
            time.sleep(10)
            self.write_result(new_centroids)
            print(f"Reducer {self.reducer_id} request completed")
            response = map_reduce_pb2.ReduceResponse(reducer_id=self.reducer_id, status="SUCCESS", new_centroids=[])
            for key in new_centroids:
                response.new_centroids.append(map_reduce_pb2.NewCentroids(centroid_id=key, point=new_centroids[key]))
            return response
        except Exception as e:
            print(f"Reducer {self.reducer_id} failed",str(e))
            return map_reduce_pb2.ReduceResponse(reducer_id=self.reducer_id, status="FAILURE")