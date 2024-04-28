import argparse
import grpc
import os
import time
from concurrent import futures
import map_reduce_pb2_grpc
from Reducer import ReducerClass


if __name__ == "__main__":
    directory = f'./Reducers'
    if not os.path.exists(directory):
        os.makedirs(directory)
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--reducer_id", type=int)
    argparser.add_argument("--port", type=int)
    argparser.add_argument("--num_mappers", type=str)
    
    reducer_id = argparser.parse_args().reducer_id
    port = argparser.parse_args().port
    num_mappers = argparser.parse_args().num_mappers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    reducer = ReducerClass(reducer_id, port, num_mappers)
    map_reduce_pb2_grpc.add_ReducerServiceServicer_to_server(reducer, server)
    server.add_insecure_port("[::]:"+str(port))
    server.start()
    print(f"Reducer {reducer_id} is running on port {port}")
    time.sleep(100)
    server.wait_for_termination(timeout=100000000000)    