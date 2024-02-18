import grpc
import notification_pb2 as notification_pb2
import notification_pb2_grpc as notification_pb2_grpc


class NotificationsStub(object):
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50052') #35.231.151.129
        self.stub = notification_pb2_grpc.NotificationsStub(self.channel)
        self.categories = {0: "ELECTRONICS", 1: "FASHION", 2: "OTHERS", 3: "ANY"}
    
    def _notify_client(self, item_id, market, client_type):
        item = market.items[item_id]
        message = "-----------------------------------\nThe following item has been updated: \n"
        message += f"Item ID: {item_id}, Name: {item.name}, Price: ${item.price}, Category: {self.categories[item.category]}\n"
        message += f"Description: {item.description}, \n"
        message += f"Quantity: {item.quantity}, \n"
        message += f"Seller ID: {item.seller_id}, Seller Address: {item.seller_address}\n"
        message += f"Rating: {item.rating} / 5\n"
        message += "-----------------------------------\n\n"
        if client_type == "BUYER":
            self.channel = grpc.insecure_channel('localhost:50053') #35.231.151.129
            self.stub = notification_pb2_grpc.NotificationsStub(self.channel)
            buyers = market.items_wishlisted[item_id]
            for buyer in buyers:
                request = notification_pb2.NotifyClientRequest(client_id=buyer.uid, item_details=message, client_address=buyer.address)
                response = self.stub.NotifyClient(request)
                print(response)
                if response.message == "SUCCESS":
                    print('SUCCESS')
                else:
                    print('FAILED')
        
        if client_type == "SELLER":
            self.channel = grpc.insecure_channel('localhost:50052') #34.139.233.234
            self.stub = notification_pb2_grpc.NotificationsStub(self.channel)
            request = notification_pb2.NotifyClientRequest(client_id=str(item.seller_id), item_details=message, client_address=item.seller_address)
            response = self.stub.NotifyClient(request)
            print(response)
            if response.message == "SUCCESS":
                print('SUCCESS')
            else:
                print('FAILED')