import random
import map_reduce_pb2
import math

def prob_gen():
        randominteger = random.randint(0, 10)
        if randominteger < 8:
            return True
        else:
            return False

def shuffle_and_sort(data):
        data.sort(key=lambda x: x.centroid_id)
        grouped_data = {}
        for d in data:
            if d.centroid_id not in grouped_data:
                grouped_data[d.centroid_id] = []
            grouped_data[d.centroid_id].append(d.point)
        return grouped_data

def get_distance(point1, point2):
        return math.sqrt(math.pow(point1.x - point2.x, 2) + math.pow(point1.y-point2.y, 2))

def get_new_centroids(grouped_data):
        new_centroids = {}
        for key in grouped_data:
            x = sum([point.x for point in grouped_data[key]])/len(grouped_data[key])
            y = sum([point.y for point in grouped_data[key]])/len(grouped_data[key])
            new_centroids[key] = map_reduce_pb2.Point(x=x, y=y)
        return new_centroids

