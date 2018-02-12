#!/usr/bin/python2.7
#coding: utf-8

import sys
import os.path
import ConfigParser
import MySQLdb.cursors

reload(sys)
sys.setdefaultencoding('utf-8')

class Database:

    def __init__(self):
        self.conn = None
        
    def getconf(self, db):
        path = os.path.dirname(__file__)
        name = 'database.cfg'
        name = os.path.join(path, name)
        config = ConfigParser.ConfigParser()
        config.read(name)
        dbms = config.get(db, 'dbms')
        host = config.get(db, 'host')
        user = config.get(db, 'user')
        password = config.get(db, 'password')
        database = config.get(db, 'database')
        if config.has_option(db, 'port'):
            port = config.get(db, 'port')
        else:
            port = ''
        if config.has_option(db, 'charset'):
            charset = config.get(db, 'charset')
        else:
            charset = 'utf8'
        return {'dbms':dbms, 'host':host, 'user':user, 'password':password, 'database':database, 'charset':charset, 'port':port}
    
    def connect(self, db):
        self.conn = None
        
        conf = self.getconf(db)
        dbms = conf['dbms']
        host = conf['host']
        user = conf['user']
        password = conf['password']
        database = conf['database']
        charset = conf['charset']
        port = conf['port']

        if dbms == 'mysql':
            port = int(port) if port else 3306
            try:
                MySQLdb = __import__('MySQLdb')
                #cursors = __import__('MySQLdb.cursors')
                conn = MySQLdb.connect(host = host, user = user, passwd = password, db = database, port=port, cursorclass=MySQLdb.cursors.DictCursor, use_unicode=True, charset='utf8')
                self.conn = conn
                self.execute('set names '+charset)
            except Exception, e:
                print e
                return None
        elif dbms == 'mssql':
            try:
                pymssql = __import__('pymssql')
                conn = pymssql.connect(host = host, user = user, password = password, database = database,  charset=charset, as_dict=true)
                self.conn = conn
            except Exception, e:
                print e
                return None
        else:
            print 'not support'
            return None
        
    def close(self):
        if self.conn != None:
            self.conn.close()
        
    def execute(self, sql, data=None):
        cur = self.conn.cursor()
        cur.execute(sql, data)
        id = self.conn.insert_id()
        cur.close()
        self.conn.commit()
        return id

    def executemany(self, sql, data):
        cur = self.conn.cursor()
        cur.executemany(sql, data)
        cur.close()
        self.conn.commit()
        
    def query(self, sql, data=None):
        cur = self.conn.cursor()
        if data:
            cur.execute(sql, data)
        else:
            cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows


    
