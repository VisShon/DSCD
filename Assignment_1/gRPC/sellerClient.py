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
from notifier import NotifierServer
from marketSeller import MarketplaceStub

class ItemInstance:

    def __init__(self, params):
        self.lock = threading.Lock()
        self.id = params.id
        self.name = params.name
        self.description = params.description
        self.price = params.price
        self.category = params.category
        self.quantity = params.quantity
        self.seller_id = params.seller_id
        self.seller_address = params.seller_address
        self.rating = 0
        self.num_ratings = 0
    
    def ratingUpdate(self, rating):
        with self.lock:
            self.rating = (self.rating * self.num_ratings + rating) / (self.num_ratings + 1)
            self.num_ratings += 1
            time.sleep(0.1)
    
    def priceUpdate(self, price):
        with self.lock:
            self.price = price
            time.sleep(0.1)

class SellerClient:

    def __init__(self, uid, address):
        self.uid = uid
        self.address = address
        self.items = {}
        self.lock = threading.Lock()
    
    def itemAdded(self, item):
        with self.lock:
            self.items[item.id] = item
            time.sleep(0.1)
    
    def itemRemoved(self, item):
        with self.lock:
            del self.items[item.id]
            time.sleep(0.1)
    
    def itemsReturn(self):
        with self.lock:
            return self.items
    


def id_gen():
    timestamp = str(int(time.time()))
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ID-{timestamp}-{random_chars}"

def init_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationsServicer_to_server(NotifierServer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":

    seller_id = uuid.uuid4()
    seller_address = "localhost:50051" #34.139.233.234

    notification_thread = threading.Thread(target=init_service, daemon=True)
    notification_thread.start()

    seller = SellerClient(seller_id, seller_address)
    print(seller)
    print("What do you want to do? ")
    print("1. Register seller")
    print("2. Sell item")
    print("3. Update item")
    print("4. Delete item")
    print("5. Display seller items")
    print("5. Exit")

    marketplace = MarketplaceStub()

    while True:
        choice = input("Enter choice: ")
        if choice == "1":
            print(seller_id)
            print(seller_address)
            marketplace.sellerRegisteration(seller)
        elif choice == "2":
            item_id = id_gen()
            name = input("Enter item name: ")
            price = float(input("Enter item price: "))
            quantity = int(input("Enter item quantity: "))
            category = input("Enter item category: ")
            description = input("Enter item description: ")
            item = ItemInstance(item_id, name, price, quantity, category, description, seller_id, seller_address)
            marketplace.itemSold(item)
        elif choice == "3":
            item_id = input("Enter item id: ")
            price = float(input("Enter new item price: "))
            quantity = int(input("Enter new item quantity: "))
            params = {"item_id": item_id, "price": price, "quantity": quantity, "seller_id": seller_id, "seller_address": seller_address}
            marketplace.itemUpdated(params)
        elif choice == "4":
            item_id = input("Enter item id: ")
            params = {"item_id": item_id, "seller_id": seller_id, "seller_address": seller_address}
            marketplace.itemRemoved(params)
        elif choice == "5":
            marketplace.itemsDisplayed(seller)
        elif choice == "6":
            break
        else:
            print("Invalid choice")
