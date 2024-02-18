import grpc
import string
import random
import time
import uuid
import threading
from concurrent import futures
import marketCentralPlatform_pb2 as mpc_pb2
import marketCentralPlatform_pb2_grpc as mpc_pb2_grpc
import notification_pb2 as notification_pb2
import notification_pb2_grpc as notification_pb2_grpc


class NotifierServer(notification_pb2_grpc.NotificationsServicer):
    def __init__(self):
        self.market = None

    def clientNotify(self, params):
        request = params.request
        context = params.context
        print("\nNew notification received...\n")
        print(request.item_details)
        try:
            return notification_pb2.clientNotifiedResp(message="SUCCESS")
        except Exception as e:
            return notification_pb2.clientNotifiedResp(message="FAILURE")