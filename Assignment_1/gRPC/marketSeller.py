import string
import threading
import time
import uuid
import grpc
from concurrent import futures
import marketCentralPlatform_pb2 as mpc_pb2
import marketCentralPlatform_pb2_grpc as mpc_pb2_grpc
import random
import notification_pb2 as notification_pb2
import notification_pb2_grpc as notification_pb2_grpc

class MarketplaceStub(object):

    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051') # 35.237.146.217
        self.stub = mpc_pb2_grpc.MarketCentralPlatformStub(self.channel)
    
    def sellerRegisteration(self, seller):
        request = mpc_pb2.sellerRegisterationRqst(id=str(seller.uid), address=seller.address)
        response = self.stub.sellerRegisteration(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')
    
    def itemSold(self, item):
        request = mpc_pb2.itemSoldRqst(id=str(item.id), name=item.name, price=item.price, quantity=item.quantity, category=item.category, description=item.description, seller_id=str(item.seller_id), seller_address=item.seller_address)
        response = self.stub.itemSold(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')
    
    def itemUpdated(self, params):
        item_id = params.item_id
        price = params.price
        quantity = params.quantity
        seller_id = params.seller_id
        seller_address = params.seller_address
        request = mpc_pb2.itemUpdatedRqst(id=str(item_id), price=price, quantity=quantity, seller_id=str(seller_id), seller_address=seller_address)
        response = self.stub.itemUpdated(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')
    
    def itemRemoved(self, params):
        item_id = params.item_id
        seller_id = params.seller_id
        seller_address = params.seller_address
        request = mpc_pb2.itemRemovedRqst(id=str(item_id), seller_id=str(seller_id), seller_address=seller_address)
        response = self.stub.itemRemoved(request)
        print(response)
        if response.message == "SUCCESS":
            print('SUCCESS')
        else:
            print('FAILED')
    
    def itemsDisplayed(self, seller):
        request = mpc_pb2.itemsDisplayedRqst(seller_id=str(seller.uid), seller_address=seller.address)
        response = self.stub.itemsDisplayed(request)
        print(response.message)