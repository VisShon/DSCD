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
from marketPlaceStub import MarketplaceStub
from notifier import NotifierServer

class BuyerClient:
    def __init__(self, uid, address):
        self.lock = threading.Lock()
        self.uid = uid
        self.address = address
        self.orders = {}
        self.wishlist = {}

    def wishlisted(self, item):
        with self.lock:
            self.wishlist[item.id] = item
            time.sleep(0.1)
    
    def carted(self, item, quantity, timestamp):
        with self.lock:
            self.orders[timestamp] = (item, quantity)
            time.sleep(0.1)

# def generate_custom_id():
#     timestamp = str(int(time.time()))
#     random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#     return f"ID-{timestamp}-{random_chars}"

def init_service():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationsServicer_to_server(NotifierServer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":

    buyer_id = uuid.uuid4()
    buyer_address = "localhost:50051" #35.231.151.129

    buyer = BuyerClient(buyer_id, buyer_address)

    notification_thread = threading.Thread(target=init_service, daemon=True)
    notification_thread.start()

    print("What do you want to do?")
    print("1. Register Buyer")
    print("2. Search Item")
    print("3. Buy Item")
    print("4. Rate Item")
    print("5. Add to Wishlist")
    print("5. Exit")

    marketplace = MarketplaceStub()

    while True:
        choice = input("Enter choice: ")
        if choice == "1":
            print(buyer_id)
            print(buyer_address)
            marketplace.buyerRegisteration(buyer)
        elif choice == "2":
            item_name = input("Enter item name: ")
            print("Enter Category from [ELECTRONICS, FASHION, OTHERS, ANY]")
            item_category = input("Enter item category: ")
            params = {"item_name": item_name, "item_category": item_category, "buyer_id": buyer_id, "buyer_address": buyer_address}
            marketplace.itemSearch(params)
        elif choice == "3":
            item_id = input("Enter item id: ")
            quantity = int(input("Enter item quantity: "))
            params = {"item_id": item_id, "buyer_id": buyer_id, "buyer_address": buyer_address, "quantity": quantity}
            marketplace.itemBought(item_id, buyer_id, buyer_address, quantity)
        elif choice == "4":
            item_id = input("Enter item id: ")
            rating = int(input("Enter rating (choose from 1 to 5): "))
            params = {"item_id": item_id, "rating": rating, "buyer": buyer}
            marketplace.itemRated(params)
        elif choice == "5":
            item_id = input("Enter item id: ")
            params = {"buyer_id": buyer_id, "buyer_address": buyer_address, "item_id": item_id}
            marketplace.itemWishlisted(params)
        elif choice == "6":
            break
        else:
            print("Invalid choice")
    