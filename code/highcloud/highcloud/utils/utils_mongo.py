#coding=utf-8

import sys
import pymongo as mongo_db
import logging
import time
import datetime
from configs import configs

class MongoUtils(object):

    db = configs['mongo']['db']
    host = configs['mongo']['host']
    port = configs['mongo']['port']
    user = configs['mongo']['user']
    password = configs['mongo']['password']

    @classmethod
    def mongo_client(cls):
        try:
            conn = mongo_db.MongoClient(host = cls.host, port = cls.port, maxPoolSize = 1000)
            db = conn[cls.db]
            db.authenticate(cls.user, cls.password)
            client = db[cls.db]

        except Exception as e:
            logging.error('MongoUtils.mongo_client Exception has occur %s' % str(sys.exc_info()[1]))
            return None
        else:
            return client

    @classmethod
    def insert_one(cls, table = None, model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            result = collection.insert_one(model_dic)
        except:
            logging.error('MongoUtils.insert_one : insert_one %s of mongodb [%s] : Exception has occured: %s' % (table, model_dic, str(sys.exc_info()[1])) )
        finally:
            return result

    @classmethod
    def insert_many(cls, table = None, model_dic_list = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            result = collection.insert_many(model_dic_list)
        except:
            logging.error('MongoUtils.insert_many : insert_many %s of mongodb %s : Exception has occured: %s' % (table, model_dic_list, str(sys.exc_info()[1])) )
        finally:
            return result

    # @classmethod
    # def query_single(cls, table = None, model_dic = None):
    #     result = []
    #     try:
    #         collection = cls.mongo_client()[table]
    #         result_single = collection.find_one(model_dic)
    #         if result:
    #             result.append(result_single)
    #     except:
    #         logging.error('MongoUtils.query_single : query_single %s of mongodb [%s] : Exception has occured: %s' % (table, model_dic, str(sys.exc_info()[1])) )
    #     finally:
    #         return result

    @classmethod
    def query(cls, table = None, model_dic = None):
        result = []
        try:
            collection = cls.mongo_client()[table]
            results = collection.find(model_dic)
            result = [data for data in results]
        except:
            logging.error('MongoUtils.query : query %s of mongodb [%s] : Exception has occured: %s' % (table, model_dic, str(sys.exc_info()[1])) )
        finally:
            return result

    @classmethod
    def replace(cls, table = None, old_model_dic = None, new_model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            result = collection.replace_one(old_model_dic, new_model_dic)
        except:
            logging.error('MongoUtils.replace : replace %s for %s to %s : Exception has occured: %s' % (table, old_model_dic, new_model_dic, str(sys.exc_info()[1])) )
        finally:
            return result

    # @classmethod
    # def replace_many(cls, table = None, model_dic_list = None):
    #     result = None
    #     try:
    #         collection = cls.mongo_client()[table]
    #         result = collection.replace_many(model_dic_list)
    #     except:
    #         logging.error('MongoUtils.replace_many : replace_many %s to %s : Exception has occured: %s' % (table, model_dic_list, str(sys.exc_info()[1])) )
    #     finally:
    #         return result

    @classmethod
    def delete_single(cls, table = None, model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            result = collection.delete_one(model_dic)
        except:
            logging.error('MongoUtils.delete_single : delete_single %s to %s : Exception has occured: %s' % (table, model_dic, str(sys.exc_info()[1])) )
        finally:
            return result

    @classmethod
    def delete(cls, table = None, model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            result = collection.delete_many(model_dic)
        except:
            logging.error('MongoUtils.delete : delete %s to %s : Exception has occured: %s' % (table, model_dic, str(sys.exc_info()[1])) )
        finally:
            return result

    @classmethod
    def update_single(cls, table = None, condition = None, model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            update_param_dic = {'set':model_dic}
            result = collection.update_one(condition, update_param_dic)
        except:
            logging.error('MongoUtils.update_single : update_single %s to %s condition %s: Exception has occured: %s' % (table, model_dic, condition, str(sys.exc_info()[1])) )
        finally:
            return result

    @classmethod
    def update(cls, table = None, condition = None, model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            update_param_dic = {'$set':model_dic}
            result = collection.update_many(condition, update_param_dic)
        except:
            logging.error('MongoUtils.update : update %s to %s condition %s: Exception has occured: %s' % (table, model_dic, condition, str(sys.exc_info()[1])) )
        finally:
            return result

    @classmethod
    def remove(cls, table = None, model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            result = collection.remove(model_dic)
        except:
            logging.error('MongoUtils.remove : remove %s of %s : Exception has occured: %s' % (table, model_dic, str(sys.exc_info()[1])) )
        finally:
            return result

    @classmethod
    def count(cls, table = None, model_dic = None):
        result = None
        try:
            collection = cls.mongo_client()[table]
            result = collection.count(model_dic)
        except:
            logging.error('MongoUtils.count : count %s of %s : Exception has occured: %s' % (table, model_dic, str(sys.exc_info()[1])) )
        finally:
            return result

if __name__ == '__main__':
    # MongoUtils.mongo_client()
    MongoUtils.insert_one(table='spider.task_id', model_dic={'a':'bcd'})
    MongoUtils.insert_many(table='spider.task_id', model_dic_list=[{'11':'11', '22':'22'}, {'33':'33', '44':'44'}])
    #  MongoUtils.replace(table='spider', old_model_dic={'00':'7'}, new_model_dic={'2':'4'})
    # MongoUtils.delete(table='spider', model_dic={'a':'bcd'})
    # MongoUtils.update(table='spider', condition = {'11':'11'}, model_dic = {'11':'100'})
    # print MongoUtils.remove(table='spider', model_dic = {'a':'adaddf'})
    # print MongoUtils.query(table='spider.123', model_dic = {'11':'100'})