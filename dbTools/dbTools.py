import json
import pymysql
from DBUtils.PooledDB import PooledDB

from .dbConfig import *

cursorclass = pymysql.cursors.DictCursor


class DBPool(object):
    __pool = None

    def __init__(self):
        """ Constructed function
        Create database connection and cursor.
        """
        self.coon = DBPool.getMysqlConn()
        self.cur = self.coon.cursor(cursor=pymysql.cursors.DictCursor)

    @staticmethod
    def getMysqlConn():
        """ Get database connection pool.
        Returns:
            __pool.connection(): the database connection pool
        """
        if DBPool.__pool is None:
            __pool = PooledDB(creator=pymysql, mincached=DB_MIN_CACHED, maxcached=DB_MAX_CACHED,
                              maxshared=DB_MAX_SHARED, maxconnections=DB_MAX_CONNECYIONS,
                              blocking=DB_BLOCKING, maxusage=DB_MAX_USAGE,
                              setsession=DB_SET_SESSION,
                              host=DB_HOST, port=DB_PORT,
                              user=DB_USER, passwd=DB_PASSWORD,
                              db=DB_DATABASE, charset=DB_CHARSET)
        return __pool.connection()

    def opModify(self, sql):
        """ Insert / Update / Delete Operator
        Args:
            sql: the sql sentence
        Returns:
            insert_num: the number of insert
        """
        insert_num = self.cur.execute(sql)  # 执行sql
        self.coon.commit()
        return insert_num

    def opSelect(self, sql):
        """ Select Operator
        Args:
            sql: the sql sentence
        Returns:
            select_res: result in the form of dict
        """
        self.cur.execute(sql)  # 执行sql
        select_res = self.cur.fetchall()  # 返回结果为字典
        return select_res

    def dispose(self):
        """ dispose the connection and close the cursor. """
        self.coon.close()
        self.cur.close()


class dbTools:
    def selectOpt(self, sql):  # select
        """ Select operator for db connection pool.
        Args:
            sql: sql sentence
            
        Returns:
            the set of results selected by sql
            example:
            [ {restaurantID: 1, restaurantName: 'rName1'},
              {restaurantID: 2, restaurantName: 'rName2'} ]
        """
        # apply connection rescource
        dbp_opt = DBPool()
        results = dbp_opt.opSelect(sql)
        dbp_opt.dispose()  # 释放连接
        return results
    def modifyOpt(self, sql):  # insert \ update \ delete
        """ Modify operator for db connection pool.
        Args:
            sql: sql sentence
            
        Returns:
            the result of modifying db
        """
        # apply connection rescource
        dbp_opt = DBPool()
        results = dbp_opt.opModify(sql)
        dbp_opt.dispose()  # 释放连接
        return results

    def signIn(self, phone_num, password):
        """ Sign in with phone_num & password.
        Args:
            phone_num: the phone number of user
            password: the password of user
            
        Returns:
            Whether success to sign in with phone_num & password.
            example:
                True / False
        """
        sql = """SELECT phone_num FROM account
                    WHERE phone_num='%s' AND password='%s' ;""" % (phone_num, password)
        results = self.selectOpt(sql)
        ID = ''
        for r in results:
            ID = r['phone_num']
        return ID != ''

    def checkKeysCorrection(self, input, valid_keys):
        """ Check whether all input keys are included in valid keys.
        Args:
            input: keys of input
            valid_keys: valid keys
            
        Returns:
            Whether all keys of input are included in valid keys.
            example:
                True / False
        """
        for key in input.keys():
            if key not in valid_keys:
                print("[ERROR] Key '%s' does not exist." % key)
                return False
            # check whether all result keys are included in valid keys
            if key == "result" and not self.checkResultsCorrection(result=input["result"], valid_keys=valid_keys):
                return False
        return True

    def checkResultsCorrection(self, result, valid_keys):
        """ Check whether all result keys are included in valid keys.
        Args:
            result: keys of result for selecting
            valid_keys: valid keys
            
        Returns:
            Whether all result keys are included in valid keys.
            example:
                True / False
        """
        for key in result:
            if key not in valid_keys:
                print("[ERROR] Key '%s' does not exist." % key)
                return False
        return True

    def getNow(self):
        """ Get the present time.
        Returns:
            now: the present time in the form of string type
            example:
                2014-04-22 15:47:06
        """
        sql = "SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%S');"
        results = self.selectOpt(sql)
        now = ''
        for r in results:
            now = r["DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%S')"]
        return now

    def getTableKeys(self, tableName):
        """ Get keys of table with name of table.
        Args:
            tableName: name of table
            
        Returns:
            resultSet: the list of names of all keys of table whose name is the value of 'tableName'
            example:
                ['restaurantID', 'restaurantName', 'password', 'phone', 'email']
        """
        sql = "SHOW COLUMNS FROM %s" % tableName
        resultSet = []
        try:
            results = self.selectOpt(sql)
            for r in results:
                resultSet.append(r['Field'])
        except:
            print("[ERROR] Table '%s' does not exist." % tableName)
        return resultSet
    
    def getConfig(self, file_name="config"):
        """ Get configuration.
        Args:
            file_name: the path of the configuration
            
        Returns:
            config: the json of configuration of database and database connection pool
        """
        with open(file_name, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
