import os
import logging
log = logging.getLogger(__file__)

import threading
import string

import pymysql.cursors

from app.core.singleton_pattern import singleton
    
class pymysql_hdlr:
    def __init__(self,hostStr,userName,password,dbName,port,identifier,dbtype="mysql",hostname=""):
        self.host = hostStr
        self.user = userName+hostname
        self.passwd = password
        self.db = dbName
        self.port = port
        self.dbtype = dbtype
        self.hostname = hostname
        self.ca_certfile = None
        self.err=''
        self.isFree=True
        self.id=identifier
        self.connect()

    def connect(self):
        try:
            # self.ca_certfile = os.path.join(os.getenv("RAD_INSTALL_DIR"),"DB_SSL_CERT","BaltimoreCyberTrustRoot.pem")
            self.conn=pymysql.connect(host = self.host, 
                                        user = self.user, 
                                        password = self.passwd, 
                                        db = self.db,
                                        port=int(self.port),
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor,
                                        # ssl={'ssl': {'ca': self.ca_certfile}}
                                        )
            self.cursor = self.conn.cursor()
            self.cursor.execute("SET AUTOCOMMIT=1") #we will enable this after we review all logics
        except pymysql.OperationalError as err:
            log.critical("-- <<MedDB>> Database Error during connection setup => %s --",str(err),exc_info=1)
            self.err=err
    
    def execute(self, qstr,command, *args):
        try:
            log.debug("<<<< Executing Query -- %s with dbhndl id=%s",qstr,str(self.id))
            log.debug("Query args:%s", args)
            # if qstr.endswith(";"):
            #     qstr = qstr[:-1]
            self.cursor.execute(qstr)
            log.debug(">>>> Executed Query -- %s with dbhndl id=%s",qstr,str(self.id))
        except pymysql.ProgrammingError as e:
            log.error("--------------------------------")
            log.error("-- Wrong Sql Statement [Exception %s] for dbhndl id=%s--",str(e),str(self.id),exc_info=1)
            log.error("Query:%s",qstr)
            log.error("Query args:%s",args)
            log.error("--------------------------------")
            return 'False',e
        except pymysql.OperationalError as e:
            # "If connection fails then "
            log.critical("-- Database Operational Error - [%s]--for dbhndl id=%s",str(e),str(self.id),exc_info=1)
            if (str(e).lower().find("2003",1,8)!=-1) or (str(e).lower().find("2013",1,8)!=-1) or (str(e).lower().find("2006",1,8)!=-1):
                try:
                    log.warn("** Trying Once Again To Connect The Database for dbhndl id=%s**",str(self.id))
                    self.connect()
                except Exception  as e:
                    return 'False',e
                else:
                    log.info('- - -Connection Restored for dbhndl id=%s- - -',str(self.id))
                    return self.execute(qstr,command, args)
            else:
                log.critical("-- Other Then Connection Lost for dbhndl id=%s- --",str(self.id))
                return 'False' ,e
        except pymysql.InternalError as e:
            #"The cursor is out of Sync"
            log.error("--------------------------------")
            log.error("-- Exception [%s]--for dbhndl id=%s",str(e),str(self.id),exc_info=1)
            log.error("Query:%s",qstr)
            log.error("Query args:%s",args)
            log.error("--------------------------------")
            return 'False',e
        except pymysql.IntegrityError as e:
            log.error("--------------------------------")
            #"a foreign key check fails, duplicate key, etc."
            log.error("-- Exception [%s]--for dbhndl id=%s",str(e),str(self.id),exc_info=1)
            log.error("Query:%s",qstr)
            log.error("Query args:%s",args)
            log.error("--------------------------------")
            return 'False',e
        except pymysql.Error as e:
            log.critical("-- Exception [%s]--for dbhndl id=%s",str(e),str(self.id),exc_info=1)
            try:
                log.info("** Trying Once Again To Connect The Database for dbhndl id=%s**",str(self.id))
                self.connect()
            except Exception  as e:
                return 'False',e
            else:
                log.info('- - -Connection Restored for dbhndl id=%s- - -',str(self.id))
                self.execute(qstr,command)
        except Exception as e:
            log.critical("-- Exception [%s]--for dbhndl id=%s",str(e),str(self.id),exc_info=1)
            return 'False',e

        # Query successful
        if command=='SELECT':
            data = self.cursor.fetchall()
            return 'True',data
        if command=='SELECT_ONE':
            data = self.cursor.fetchone()
            return 'True',data
        elif command=='UPDATE':
            #  Unlock Tables Explicitly 
            rowcount=self.cursor.rowcount
            #log.debug("Calling commit() after UPDATE from meddb.py on every successful update")
            #stat,row = self.commit()
            return 'True',rowcount
        elif command=='DELETE':
            #  Unlock Tables Explicitly 
            rowcount=self.cursor.rowcount
            #stat = self.unlockTables()
            return 'True',rowcount
        elif command=='INSERT':	    
            return 'True','Inserted',self.cursor.lastrowid
        elif command=='EXECUTE':
            return 'True','Executed'
        elif command=='START TRANS':
            return 'True','Started'
        #elif command=='ROLLBACK':
        #    return 'True','Rollback'
        elif command=='COMMIT':
            return 'True','Commit'
        #elif command=='savepoint':
        #    return 'True','savepoint'
        #elif command=='COMMIT TRANS':
        #    return 'True','Transaction Commit'
        #elif command=='ROLLTRANS':
        #    return 'True','Transaction Rolled'
        else:
            log.critical("Unsupported SQL command = %s",command)


@singleton
class dbHdlr:
    def __init__(self):
        self.dbHndlrList=[]
        self.lock = threading.Lock()
        for i in range(1,int(os.getenv("DB_POOL_SIZE"))+1):
            dbHndlr_obj = pymysql_hdlr(os.getenv("DB_HOST"), os.getenv("DB_USER"),
            os.getenv("DB_PASS"), os.getenv("DB_NAME"), int(os.getenv("DB_PORT")),i,
            dbtype=os.getenv("DB_TYPE"), 
            hostname=os.getenv("DB_FQDN",""))
            if dbHndlr_obj is not None and dbHndlr_obj.err == '':
                self.dbHndlrList.append(dbHndlr_obj)
        log.info("Initialized DB Pool")

    def select_one(self,qstr, *args):
        dbhndl_obj = None
        self.lock.acquire()
        try:
            for tmp_obj in self.dbHndlrList :
                if tmp_obj.isFree == True:
                    dbhndl_obj = tmp_obj
                    dbhndl_obj.isFree = False
                    #log.info("Found idle dbhandle id = %s",str(dbhndl_obj.id))
                    break
        except Exception as e:
            log.critical("Exception During Database selection=%s",str(e))
        self.lock.release()
        if  dbhndl_obj == None:
            log.error("No dbhandle free....CANNOT PROCEED")
            return 'False',None
        try:
            print(args)
            stat,rowset = dbhndl_obj.execute(qstr,'SELECT_ONE', args)
            print("rowset:{}".format(rowset))
        except Exception as e:
            print(e)
            print("*"*100)
            return False, None
        dbhndl_obj.isFree = True
        return stat,rowset

    def select(self,qstr, *args):
        dbhndl_obj = None
        self.lock.acquire()
        try:
            for tmp_obj in self.dbHndlrList :
                if tmp_obj.isFree == True:
                    dbhndl_obj = tmp_obj
                    dbhndl_obj.isFree = False
                    #log.info("Found idle dbhandle id = %s",str(dbhndl_obj.id))
                    break
        except Exception as e:
            log.critical("Exception During Database selection=%s",str(e))
        self.lock.release()
        if  dbhndl_obj == None:
            log.error("No dbhandle free....CANNOT PROCEED")
            return 'False',None
        stat,rowset = dbhndl_obj.execute(qstr,'SELECT', args)
        dbhndl_obj.isFree = True
        return stat,rowset

        
    def update(self,qstr, *args):
        #stat,rowset = self.execute("SAVEPOINT aa",'savepoint')
        #stat,rowset = self.execute(qstr,'UPDATE')
        dbhndl_obj = None
        self.lock.acquire()
        try:
            for tmp_obj in self.dbHndlrList :
                if tmp_obj.isFree == True:
                    dbhndl_obj = tmp_obj
                    dbhndl_obj.isFree = False
                    #log.info("Found idle dbhandle id = %s",str(dbhndl_obj.id))
                    break
        except Exception as e:
            log.critical("Exception During free database handle selection=%s",str(e))
        self.lock.release()
        if  dbhndl_obj == None:
            log.error("No dbhandle free....CANNOT PROCEED")
            return 'False',None
        stat,rowset = dbhndl_obj.execute(qstr,'UPDATE', *args)
        dbhndl_obj.isFree = True
        return stat,rowset

    
    def delete(self,qstr, *args):
        #stat,rowset = self.execute("SAVEPOINT aa",'savepoint')        
        #stat,rowset = self.execute(qstr,'DELETE')
        dbhndl_obj = None
        self.lock.acquire()
        try:
            for tmp_obj in self.dbHndlrList :
                if tmp_obj.isFree == True:
                    dbhndl_obj = tmp_obj
                    dbhndl_obj.isFree = False
                    #log.info("Found idle dbhandle id = %s",str(dbhndl_obj.id))
                    break
        except Exception as e:
            log.critical("Exception During Database selection=%s",str(e))
        self.lock.release()
        if  dbhndl_obj == None:
            log.error("No dbhandle free....CANNOT PROCEED")
            return 'False',None
        stat,rowset = dbhndl_obj.execute(qstr,'DELETE', args)
        dbhndl_obj.isFree = True
        return stat,rowset
    
    def insert(self,qstr, *args):
        #stat,rowset = self.execute("SAVEPOINT aa",'savepoint')        
        #stat,rowset = self.execute(qstr,'INSERT')
        dbhndl_obj = None
        self.lock.acquire()
        try:
            for tmp_obj in self.dbHndlrList :
                if tmp_obj.isFree == True:
                    dbhndl_obj = tmp_obj
                    dbhndl_obj.isFree = False
                    #log.info("Found idle dbhandle id = %s",str(dbhndl_obj.id))
                    break
        except Exception as e:
            log.critical("Exception During Database selection=%s",str(e))
        self.lock.release()
        if  dbhndl_obj == None:
            log.error("No dbhandle free....CANNOT PROCEED")
            return 'False',None
        try:
            stat,rowset,rowid = dbhndl_obj.execute(qstr,'INSERT', *args)        
        except Exception as e:
            stat,rowset,rowid = False, None, -1
        finally:
            dbhndl_obj.isFree = True
        return stat,rowset,rowid
    
    #def execute(self, qstr):
    #   stat,rowset = self.execute(qstr,'EXECUTE')
    #    return stat,rowset
    
    def commit(self):
        #stat,rowset = self.execute("COMMIT",'COMMIT')
        #return stat,rowset
        return 'True','Commit'
    
    #def rollback(self):
    #   stat,rowset = self.execute("ROLLBACK TO SAVEPOINT aa",'ROLLBACK')
    #    return stat,rowset
    
    #def startTrans(self):
    #    stat,rowset = self.execute("START TRANSACTION",'START TRANS')
    #    stat,rowset = self.execute("SAVEPOINT bb",'START TRANS')
    #    return stat, rowset
    
    #def rollTrans(self):
    #    stat,rowset = self.execute("ROLLBACK TO SAVEPOINT bb",'ROLLTRANS')
    #    return stat,rowset
    
    #def commitTrans(self):
    #    stat,rowset = self.execute("COMMIT",'COMMIT TRANS')
    #    return stat,rowset
    
    def close(self):
        self.cursor.close()
        self.conn.close()

