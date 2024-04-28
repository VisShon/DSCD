import grpc
import argparse
from concurrent import futures
import map_reduce_pb2_grpc
from Mapper import MapperClass

if __name__=='__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--mapper_id", type=int)
    argparser.add_argument("--port", type=int)
    argparser.add_argument("--num_reducers", type=int)
    
    mapper_id = argparser.parse_args().mapper_id
    port = argparser.parse_args().port
    num_reducers = argparser.parse_args().num_reducers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    mapper = MapperClass(mapper_id, port, num_reducers)
    map_reduce_pb2_grpc.add_MapperServiceServicer_to_server(mapper, server)
    server.add_insecure_port("[::]:"+str(port))
    server.start()
    print(f"Mapper {mapper_id} is running on port {port}")
    server.wait_for_termination(timeout=10000000000)