import os

import pymongo as pm

LOCAL = "0"
CLOUD = "1"

JOURNAL_DB = 'teamasare'
USERS_COLLECTION = 'users'

client = None

MONGO_ID = '_id'


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print("Setting client because it is None.")
        if os.environ.get("CLOUD_MONGO", LOCAL) == CLOUD:
            password = os.environ.get("JOURNAL_DB_PW")
            if not password:
                raise ValueError('You must set your password '
                                 + 'to use Mongo in the cloud.')
            print("Connecting to Mongo in the cloud.")
            client = pm.MongoClient(f'mongodb+srv://teamasare:{password}'
                                    + '@cluster0.ib3jg.mongodb.net/?'
                                    + 'retryWrites=true&w='
                                    + 'majority&appName=Cluster0',
                                    tls=True,
                                    connectTimeoutMS=30000,
                                    socketTimeoutMS=None,
                                    connect=False,
                                    maxPoolSize=1)

        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        doc[MONGO_ID] = str(doc[MONGO_ID])


def insert_one(collection, doc, db=JOURNAL_DB, testing=False):
    """
    Insert a single doc into collection.
    """
    return client[db][collection].insert_one(doc)


def fetch_one(collection, filt, db=JOURNAL_DB, testing=False):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        if MONGO_ID in doc:
            # Convert mongo ID to a string so it works as JSON
            doc[MONGO_ID] = str(doc[MONGO_ID])
        return doc


def del_one(collection, filt, db=JOURNAL_DB, testing=False):
    """
    Find with a filter and return on the first doc found.
    """
    client[db][collection].delete_one(filt)


def update_doc(collection, filters, update_dict, db=JOURNAL_DB, testing=False):
    return client[db][collection].update_one(filters, {'$set': update_dict})


def fetch_all(collection, db=JOURNAL_DB, testing=False):
    ret = []
    for doc in client[db][collection].find():
        ret.append(doc)
    return ret


def fetch_all_as_dict(key, collection, db=JOURNAL_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret
