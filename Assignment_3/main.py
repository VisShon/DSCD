import os
import shutil
import grpc
import map_reduce_pb2_grpc
from Master import Master
from concurrent import futures

def reset():
    if os.path.exists('./Mappers'):
        shutil.rmtree('./Mappers')
    if os.path.exists('./Reducers'):
        shutil.rmtree('./Reducers')

def mapReduceKmeans(num_mappers,num_reducers,num_centroids,max_iters):
    master = Master(num_mappers,num_reducers,num_centroids,max_iters)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    map_reduce_pb2_grpc.add_MasterServiceServicer_to_server(master, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    master.run()
    

def main():
    num_reducers = int(input("Enter Reducers Count: "))
    num_mappers = int(input("Enter Mappers Count: "))
    max_iters = int(input("Enter no. of Iterations: "))
    num_centroids = int(input("Enter no. of Centroids: "))
    reset()
    mapReduceKmeans(num_mappers,num_reducers,num_centroids,max_iters)


if __name__=='__main__':
    main()
    
    
    