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

class MarketplaceStub(object):
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051') #35.237.146.217
        self.stub = mpc_pb2_grpc.MarketCentralPlatformStub(self.channel)

    def buyerRegisteration(self, buyer):
        request = mpc_pb2.buyerRegisterationRqst(id=str(buyer.uid), address=buyer.address)
        response = self.stub.buyerRegisteration(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')
    
    def itemSearch(self, params):
        item_name = params.item_name
        item_category = params.item_category
        buyer_id = params.buyer_id
        buyer_address = params.buyer_address

        request = mpc_pb2.itemSearchRqst(name=item_name, category=item_category, buyer_id=str(buyer_id), buyer_address=buyer_address)
        response = self.stub.itemSearch(request)
        print(response.message)

    def itemBought(self, params):
        item_id = params.item_id
        buyer_id = params.buyer_id
        buyer_address = params.buyer_address
        item_quantity = params.item_quantity

        request = mpc_pb2.itemBoughtRqst(item_id=str(item_id), buyer_id=str(buyer_id), buyer_address=buyer_address, item_quantity=item_quantity)
        response = self.stub.itemBought(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')
    
    def itemRated(self, params):
        item_id = params.item_id
        rating = params.rating
        buyer = params.buyer

        request = mpc_pb2.itemRatedRqst(item_id=str(item_id), rating=rating, buyer_id=str(buyer.uid), buyer_address=buyer.address)
        response = self.stub.itemRated(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')

    def itemWishlisted(self, params):
        buyer_id = params.buyer_id
        buyer_address = params.buyer_address
        item_id = params.item_id

        request = mpc_pb2.itemWishlistedRqst(buyer_id = str(buyer_id), buyer_address=buyer_address, item_id = str(item_id))
        response = self.stub.itemWishlisted(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')

