#from pymongo import MongoClient
# pip install pymongo
# pip install dnspython
from pymongo import MongoClient

'''
def test_connection():
    client = pymongo.MongoClient("mongodb+srv://irad:n4th4n123@irad-cluster-nouuy.mongodb.net/test?retryWrites=true&w=majority")
    db = client.irad.dicom
    print(db.command("serverStatus"))
    '''


def init_connection():
    client = MongoClient(
        "mongodb+srv://irad:n4th4n123@irad-cluster-nouuy.mongodb.net/test?retryWrites=true&w=majority")
    db = client.irad.dicom
    return db


def init_docker_localhost():
    client = MongoClient("mongodb://localhost:27017")
    db = client.admin
    return db
