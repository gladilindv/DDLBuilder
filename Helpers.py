# coding: cp1251

# import ibm_db

# local
import Config


class DataBaseMgr:
    def __init__(self, aRgn):
        self.mRgn = aRgn
        self.mConn = None
        self.mTable = "PDC.INSTALLED_SCRIPTS"

    def connect(self, aEnv):
        self.mTable = Config.getDBTableName(aEnv, self.mRgn)
        dataSource = Config.getDBDataSource(aEnv, self.mRgn)

        print ("[INF] connecting to ({0} : {1})".format(dataSource, dataTable))

        try:
            self.mConn = ibm_db.connect(dataSource, Config.db_deploy_user, Config.db_deploy_pass)
        except:
            print ("[ERR] DB error({0})".format(ibm_db.conn_errormsg()))

    def getInstalledSQLScripts(self):
        """
        Возвращает словарь установленных скриптов вместе с md5
        """
        installed = {}

        if self.mConn is None:
            return installed

        sql = "select * from " + self.mTable + " order by SCRIPT_NAME"

        try:
            stmt = ibm_db.exec_immediate(self.mConn, sql)
        except:
            print ("[ERR] DB error({0})".format(ibm_db.stmt_errormsg()))
            return installed

        row = ibm_db.fetch_assoc(stmt)
        while row:
            name = row["SCRIPT_NAME"]
            md5 = row["SCRIPT_MESSAGE"]

            installed[name] = md5

            row = ibm_db.fetch_assoc(stmt)

        return installed

    def isObjectExist(self, aSQL):
        if self.mConn is None:
            return False

        try:
            stmt = ibm_db.exec_immediate(self.mConn, aSQL)
        except:
            print ("[ERR] DB error({0})".format(ibm_db.stmt_errormsg()))

        # TODO
        # row = ibm_db.fetch_assoc(stmt)
        # fetch count row
        # return count > 1
        return True

    def isTableExist(self, aName, aType):
        schema, name = aName.split('.')
        sql = "select 1 from SYSCAT.TABLES where TABSCHEMA='{0}' and TABNAME='{1}' and TYPE='{2}'".format(schema, name, aType)

        return self.isObjectExist(sql)

    def isTriggerExist(self, aName):
        schema, name = aName.split('.')
        sql = "select 1 from SYSCAT.TRIGGERS where TRIGSCHEMA='{0}' and TRIGNAME='{1}'".format(schema, name)

        return self.isObjectExist(sql)

    def isIndexExist(self, aName):
        schema, name = aName.split('.')
        sql = "select 1 from SYSCAT.INDEXES where INDSCHEMA='{0}' and INDNAME='{1}'".format(schema, name)

        return self.isObjectExist(sql)

    def isRoutineExist(self, aName, aType):
        schema, name = aName.split('.')
        sql = "select 1 from SYSCAT.ROUTINES where ROUTINESCHEMA='{0}' and ROUTINENAME='{1}'".format(schema, name)

        # TODO
        # check and parse parameters

        return self.isObjectExist(sql)

    def isSpecRoutineExist(self, aName, aType):
        schema, name = aName.split('.')
        sql = "select 1 from SYSCAT.ROUTINES where ROUTINESCHEMA='{0}' and SPECIFICNAME='{1}' and ROUTINETYPE='{2}'".format(schema, name, aType)

        return self.isObjectExist(sql)
