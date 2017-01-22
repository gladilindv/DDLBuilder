# coding: cp1251

# additional modules
#import ibm_db

# local
import Config


class DataBaseMgr:
    def __init__(self, aRgn):
        self.mRgn = aRgn


    def getInstalledSQLScripts(self, aEnv):

        """
        Возвращает словарь установленных скриптов вместе с md5
        env - среда для сборки
        """
        dict = {}

        dataSource = Config.getDBDataSource(aEnv, self.mRgn)
        dataTable = Config.getDBTableName(aEnv, self.mRgn)

        print ("[INF] connecting to ({0} : {1})".format(dataSource, dataTable))

        return dict

        try:
            ibm_db_conn = ibm_db.connect(dataSource, Config.db_deploy_user, Config.db_deploy_pass)
        except:
            print ("[ERR] DB error({0})".format(ibm_db.conn_errormsg()))
            return dict

        sql = "select * from " + dataTable + " order by SCRIPT_NAME"

        try:
            stmt = ibm_db.exec_immediate(ibm_db_conn, sql)
        except:
            print ("[ERR] DB error({0})".format(ibm_db.stmt_errormsg()))
            return dict

        row = ibm_db.fetch_assoc(stmt)
        while row:
            name = row["SCRIPT_NAME"]
            md5 = row["SCRIPT_MESSAGE"]

            dict[name] = md5

            row = ibm_db.fetch_assoc(stmt)

        return dict
