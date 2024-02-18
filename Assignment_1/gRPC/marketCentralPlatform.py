import grpc
import time
import threading
from concurrent import futures
import marketCentralPlatform_pb2 as mpc_pb2
import marketCentralPlatform_pb2_grpc as mpc_pb2_grpc
import notification_pb2 as notification_pb2
import notification_pb2_grpc as notification_pb2_grpc
from marketServer import MarketCentralPlatform

class Market:
    def __init__(self):
        self.lock = threading.Lock()
        self.buyers = {}
        self.sellers = {}
        self.items = {}
        self.wishlist = {}
    
    def sellerRegisteration(self, seller):
        with self.lock:
            print(f"Seller join request from {seller.address} uuid: {seller.uid}")
            if seller.uid in self.sellers:
                print("----------------------")
                return False
            self.sellers[seller.uid] = seller
            time.sleep(0.1)
            print(self.sellers)
            print("----------------------")
            return True
    
    def itemSold(self, item):
        with self.lock:
            print(f"Sell Item request from {item.seller_address}")
            if item.id in self.items:
                print("----------------------")
                return False
            if item.seller_id not in self.sellers:
                print("----------------------")
                return False
            self.items[item.id] = item
            print("Item Added")
            self.sellers[item.seller_id].add_item(item)
            time.sleep(0.1)
            print(self.items)
            self.wishlist[item.id] = []
            print("----------------------")
            return True
    
    def itemUpdated(self, params):
        item_id = params.item_id
        new_price = params.new_price
        new_quantity = params.new_quantity
        seller_id = params.seller_id
        seller_address = params.seller_address
        with self.lock:
            print(f"Update Item {item_id} request from {seller_address}")
            if item_id not in self.items:
                print("----------------------")
                return False
            if seller_id not in self.sellers:
                print("----------------------")
                return False
            else:
                seller_items = self.sellers[seller_id].get_items()
                if item_id not in seller_items:
                    return False
            item = self.items[item_id]
            print(f"Before: {item.price} {item.quantity} ")
            item.price = new_price
            item.quantity = new_quantity
            
            self.items[item_id] = item
            print(f"After: {item.price} {item.quantity} ")
            print("----------------------")
            time.sleep(0.1)
            return True
        
    def itemRemoved(self, params):
        item_id, seller_id, seller_address = params.item_id, params.seller_id, params.seller_address
        with self.lock:
            print(f"Delete Item {item_id} request from {seller_address}")
            print(f"Item Exists: {item_id in self.items}")
            if item_id not in self.items:
                print("----------------------")
                return False
            if seller_id not in self.sellers:
                print("----------------------")
                return False
            else:
                seller_items = self.sellers[seller_id].get_items()
                if item_id not in seller_items:
                    print("----------------------")
                    return False
            del self.items[item_id]
            del self.sellers[seller_id].items[item_id]
            del self.wishlist[item_id]
            print(f"Item Exists: {item_id in self.items}")
            print("----------------------")
            time.sleep(0.1)
            return True
    
    def itemsDisplayed(self, seller):
        with self.lock:
            print(f"Display Seller Items request from {seller.address}, UUID: {seller.uid}")
            result = {}
            if seller.uid not in self.sellers:
                result = {}
            else:
                result = self.sellers[seller.uid].get_items()
            print(result)
            print("----------------------")
            return result
    
    def buyerRegisteration(self, buyer):
        with self.lock:
            print(f"Buyer join request from {buyer.address} uuid: {buyer.uid}")
            if buyer.uid in self.buyers:
                print("----------------------")
                return False
            self.buyers[buyer.uid] = buyer
            print(self.buyers)
            print("----------------------")
            return True
    
    def itemSearch(self, params):
        item_name, category, client = params.item_name, params.category, params.client
        with self.lock:
            result = []
            category_dict = {0: "ELECTRONICS", 1: "FASHION", 2: "OTHERS", 3: "ANY"}
            if item_name == "":
                item_name = "<EMPTY>"
            print(f"Search Item request Item Name: {item_name} Category: {category_dict[category]} from Client: {client.address}")
            if item_name == "<EMPTY>":
                if category == 3:
                    print(self.items.values())
                    result = list(self.items.values())
                else:
                    print("HERE")
                    for item in self.items.values():
                        print(item.category, category_dict[category])
                        if item.category == category:
                            print("HELLO")
                            result.append(item)
            else:
                if category == 3:
                    for item in self.items.values():
                        if item.name == item_name:
                            result.append(item)
                else:
                    for item in self.items.values():
                        if item.name == item_name and item.category == category:
                            result.append(item)
            print(result)
            print("----------------------")
            return result
        
    def itemBought(self, params):
        buyer, item_id, quantity = params.buyer, params.item_id, params.quantity
        with self.lock:
            print(f"Buy Item request from {buyer.address} for Item ID: {item_id} Quantity: {quantity}")
            print("1")
            if item_id not in self.items:
                print("----------------------")
                return False
            if buyer.uid not in self.buyers:
                self.buyers[buyer.uid] = buyer
            item = self.items[item_id]
            if item.quantity < quantity:
                print("----------------------")
                return False
            item.quantity -= quantity
            timestamp = str(int(time.time()))
            buyer.add_to_cart(item, quantity, timestamp)
            print("----------------------")
            time.sleep(0.1)
            return True
    
    def itemWishlisted(self, params):
        buyer, item_id = params.buyer, params.item_id
        with self.lock:
            print(f"Wishlist request from {buyer.address} for Item ID: {item_id}")
            if item_id not in self.items:
                print("----------------------")
                return False
            if buyer.uid not in self.buyers:
                self.buyers[buyer.uid] = buyer
            item = self.items[item_id]
            buyer.add_to_wishlist(item)
            self.wishlist[item_id].append(buyer)
            print("----------------------")
            time.sleep(0.1)
            return True
    
    def itemRated(self, params):
        buyer, item_id, rating = params.buyer, params.item_id, params.rating
        with self.lock:
            print(f"Rate Item request from {buyer.address} for Item ID: {item_id} Rating: {rating}")
            if item_id not in self.items:
                print("----------------------")
                return False
            item = self.items[item_id]
            item.update_rating(rating)
            print("----------------------")
            time.sleep(0.1)
            return True
    
    def clientNotified(self, params):
        item_id, client_type = params.item_id, params.client_type
        with self.lock:
            if item_id not in self.items:
                return False
            item = self.items[item_id]
            if client_type == "BUYER":
                for buyer in self.wishlist[item_id]:
                    pass
            elif client_type == "SELLER":
                seller = self.sellers[item.seller_id]
                pass
            time.sleep(0.1)
            return True



def init_service(market):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mpc_pb2_grpc.add_MarketCentralPlatformServicer_to_server(MarketCentralPlatform(market), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    market = Market()
    print("Market Server Initiated")
    init_service(market)