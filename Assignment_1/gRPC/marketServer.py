import grpc
from concurrent import futures
import sellerClient
import buyerClient
from notificationsStub import NotificationsStub
import marketCentralPlatform_pb2 as mcp_pb2
import marketCentralPlatform_pb2_grpc as mcp_pb2_grpc
import notification_pb2 as notification_pb2
import notification_pb2_grpc as notification_pb2_grpc

class MarketCentralPlatform(mcp_pb2_grpc.MarketCentralPlatformServicer):
    def __init__(self, market):
        self.market = market
        self.notifier = NotificationsStub()
        self.categories = {0: "ELECTRONICS", 1: "FASHION", 2: "OTHERS", 3: "ANY"}
    
    def buyerRegisteration(self, params):
        request = params.request
        client = buyerClient.Buyer(request.id, request.address)
        print(request)
        try:
            res = self.market.register_buyer(client)
            if not res:
                return mcp_pb2.buyerRegisterationResp(message="FAILURE")
            return mcp_pb2.buyerRegisterationResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.buyerRegisterationResp(message="FAILURE")

    def itemSearch(self, params):
        request = params.request
        address = request.buyer_address
        client = buyerClient.Buyer(request.buyer_id, address = address)
        print(request)
        try:
            items = self.market.search_item(request.name, request.category, client)
            response = "-----------------------------------\n\n"
            for item in items:
                response += f"Item ID: {item.id}, Name: {item.name}, Price: ${item.price}, Category: {self.categories[item.category]} \n"
                response += f"Description: {item.description}, \n"
                response += f"Quantity: {item.quantity}, \n"
                response += f"Seller ID: {item.seller_id}, Seller Address: {item.seller_address}\n"
                response += f"Rating: {item.rating} / 5\n"
                response += "-----------------------------------\n\n"
            return mcp_pb2.itemSearchResp(message=response)
        except Exception as e:
            return mcp_pb2.itemSearchResp(message="Error!")

    def itemBought(self, params):
        request = params.request
        address = request.buyer_address
        client = buyerClient.Buyer(request.buyer_id, address=address)
        print(request)
        try:
            res = self.market.buy_item(client, request.item_id, request.item_quantity)
            if not res:
                return mcp_pb2.itemBoughtResp(message="FAILURE")
            print("HELLO")
            self.notifier._notify_client(request.item_id, self.market, "SELLER")
            return mcp_pb2.itemBoughtResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.itemBoughtResp(message="FAILURE")

    def itemWishlisted(self, params):
        request = params.request
        address = request.buyer_address
        client = buyerClient.Buyer(request.buyer_id, address=address)
        print(request)
        try:
            res = self.market.itemWishlisted(client, request.item_id)
            if not res:
                return mcp_pb2.itemBoughtResp(message="FAILURE")
            return mcp_pb2.itemBoughtResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.itemBoughtResp(message="FAILURE")

    def itemRated(self, params):
        request = params.request
        address = request.buyer_address
        client = buyerClient.Buyer(request.buyer_id, address=address)
        print(request)
        try:
            res = self.market.itemRated(client, request.item_id, request.rating)
            print(res, "RESULT")
            if not res:
                return mcp_pb2.itemBoughtResp(message="FAILURE")
            return mcp_pb2.itemBoughtResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.itemBoughtResp(message="FAILURE")
    
    def sellerRegisteration(self, request, context):
        address = request.address
        seller_obj = sellerClient.Seller(request.id, address=address)
        print(request)
        try:
            res = self.market.sellerRegisteration(seller_obj)
            if not res:
                return mcp_pb2.sellerRegisterationResp(message="FAILURE")
            return mcp_pb2.sellerRegisterationResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.sellerRegisterationResp(message="FAILURE")
    
    def itemSold(self, params):
        request = params.request
        address = request.seller_address
        item_obj = sellerClient.Item(request.id, request.name, request.price, request.quantity, request.category, request.description, request.seller_id, address)
        print(request)
        try:
            res = self.market.sell_item(item_obj)
            if not res:
                return mcp_pb2.itemSoldResp(message="FAILURE")
            return mcp_pb2.itemSoldResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.itemSoldResp(message="FAILURE")
    
    def itemUpdated(self, params):
        request = params.request
        address = request.seller_address
        print(request)
        try:
            result = self.market.itemUpdated(request.id, request.price, request.quantity, request.seller_id, address)
            if not result:
                return mcp_pb2.itemUpdatedResp(message="FAILURE")
            self.notifier._notify_client(request.id, self.market, "BUYER")
            return mcp_pb2.itemUpdatedResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.itemUpdatedResp(message="FAILURE")
    
    def itemRemoved(self, params):
        request = params.request
        address = request.seller_address
        item_id = request.id
        print(request)
        try:
            result = self.market.itemRemoved(item_id, request.seller_id, address)
            if not result:
                return mcp_pb2.itemRemovedResp(message="FAILURE")
            return mcp_pb2.itemRemovedResp(message="SUCCESS")
        except Exception as e:
            return mcp_pb2.itemRemovedResp(message="FAILURE")
    
    def itemsDisplayed(self, params):
        request = params.request
        address = request.seller_address
        seller_obj = sellerClient.Seller(request.seller_id, address)
        print(request)
        try:
            items = self.market.display_seller_items(seller_obj)
            response = "-----------------------------------\n\n"
            for item_id, item in items.items():
                response += f"Item ID: {item_id}, Name: {item.name}, Price: ${item.price}, Category: {self.categories[item.category]}\n"
                response += f"Description: {item.description}, \n"
                response += f"Quantity: {item.quantity}, \n"
                response += f"Seller ID: {item.seller_id}, Seller Address: {item.seller_address}\n"
                response += f"Rating: {item.rating} / 5\n"
                response += "-----------------------------------\n\n"
            return mcp_pb2.itemsDisplayedResp(message=response)
        except Exception as e:
            return mcp_pb2.itemsDisplayedResp(message="Error!")