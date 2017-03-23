# coding: cp1251

import ibm_db

# local
import Config


class DataBaseMgr:
    def __init__(self, aRgn):
        self.mRgn = aRgn
        self.mErr = ""
        self.mConn = None
        self.mTable = "PDC.INSTALLED_SCRIPTS"

    def connect(self, aEnv):
        self.mTable = Config.getDBTableName(aEnv, self.mRgn)
        dataSource = Config.getDBDataSource(aEnv, self.mRgn)

        print ("[INF] connecting to {0}::{1}".format(dataSource, self.mTable))

        try:
            self.mConn = ibm_db.connect(dataSource, Config.db_deploy_user, Config.db_deploy_pass)
        except:
            self.mErr = ibm_db.conn_errormsg()
            print ("[ERR] DB error({0})".format(self.mErr.splitlines()))

        return self.mConn is not None

    def disconnect(self):
        if self.mConn is None:
            return
        ibm_db.close(self.mConn)
        self.mConn = None

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

        row = ibm_db.fetch_row(stmt)
        return row

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
        if aName.find('(') == -1:
            schema, name = aName.split('.')
            sql = "select 1 from SYSCAT.ROUTINES where ROUTINESCHEMA='{0}' and ROUTINENAME='{1}'".format(schema, name)

            return self.isObjectExist(sql)

        s = aName.index('(')
        e = aName.index(')')

        schema, name = aName[:s].split('.')
        argstr = aName[s+1:e]

        arglst = []
        argraw = argstr.split(',')
        for arg in argraw:
            if arg == "CHAR":
                arg = "CHARACTER"
            elif arg == "INT":
                arg = "INTEGER"
            elif arg == "DEC":
                arg = "DECIMAL"
            elif arg == "NUM":
                arg = "NUMERIC"

            arglst.append(arg)

        sql = "select 1 from (select R.ROUTINESCHEMA, R.ROUTINENAME, R.SPECIFICNAME, R.ROUTINETYPE, " \
              "coalesce(listagg(" \
              "replace(P.TYPENAME, ' ','') || case " \
              "when P.TYPENAME in ('CHARACTER','VARCHAR','LONG VARCHAR') then '(' || rtrim(char(P.LENGTH)) || ')' " \
              "when P.TYPENAME in ('DECIMAL') then '(' || rtrim(char(P.LENGTH)) || ',' || rtrim(char(P.SCALE)) || ')' " \
              "else '' end" \
              ", ',') within group (order by P.ORDINAL asc), '') as PARAMS " \
              "from SYSCAT.ROUTINES R " \
              "left outer join SYSCAT.ROUTINEPARMS P on P.ROUTINESCHEMA=R.ROUTINESCHEMA and " \
              "P.SPECIFICNAME=R.SPECIFICNAME and P.ORDINAL > 0 " \
              "where " \
              "R.ROUTINESCHEMA='{0}' " \
              "group by R.ROUTINESCHEMA, R.ROUTINENAME, R.SPECIFICNAME, R.ROUTINETYPE) A " \
              "where A.ROUTINENAME='{1}' " \
              "and A.PARAMS='{2}' " \
              "and A.ROUTINETYPE='{3}'".format(schema, name, ','.join(arglst), aType)

        return self.isObjectExist(sql)

    def isSpecRoutineExist(self, aName, aType):
        schema, name = aName.split('.')
        sql = "select 1 from SYSCAT.ROUTINES where ROUTINESCHEMA='{0}' and SPECIFICNAME='{1}' and ROUTINETYPE='{2}'".format(schema, name, aType)

        return self.isObjectExist(sql)
