# coding: cp1251

db_deploy_user = "srv-ps-builder"
db_deploy_pass = "C,jhjxysqRjydtqth"

db_ddl_placeholders = ["'$RCI_SRV_USER$'"]
db_grant_placeholders = ["$DB2_USER_NAME$", "$PDC_SUPPORT_GROUP$"]

db_users = {
    "AA":
        {"MSK": {"$DB2_USER_NAME$": "SRV_TST_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "KRD": {"$DB2_USER_NAME$": "SRV_TST_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"}},
    "CC":
        {"MSK": {"$DB2_USER_NAME$": "SRV_TST_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "KRD": {"$DB2_USER_NAME$": "SRV_TST_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"}},
    "DD":
        {"MSK": {"$DB2_USER_NAME$": "SRV_TST_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "KRD": {"$DB2_USER_NAME$": "SRV_TST_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"}},
    "PROD":
        {"MSK": {"$DB2_USER_NAME$": "SRV_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "KRD": {"$DB2_USER_NAME$": "SRV_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "NNV": {"$DB2_USER_NAME$": "SRV_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "EKB": {"$DB2_USER_NAME$": "SRV_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "NSK": {"$DB2_USER_NAME$": "SRV_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"},
         "SPB": {"$DB2_USER_NAME$": "SRV_PDC", "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO"}}
}

db_host = {
    "AA": "",
    "CC": "",
    "DD": "",
    "PROD": ""

}

db_insts = {
    "AA":
        {"MSK": {"$INST$": "RBAPRV01", "$TBL$": "PDC.INSTALLED_SCRIPTS"},
         "KRD": {"$INST$": "KRDDB_A2", "$TBL$": "PDC.INSTALLED_SCRIPTS"}},
    "CC":
        {"MSK": {"$INST$": "RBATST02", "$TBL$": "PDC.INSTALLED_SCRIPTS"},
         "KRD": {"$INST$": "KRDDB_CP", "$TBL$": "PDC.INSTALLED_SCRIPTS"}},
    "DD":
        {"MSK": {"$INST$": "RBADBTS1", "$TBL$": "PDC.INSTALLED_SCRIPTS"},
         "KRD": {"$INST$": "KRDDB_D2", "$TBL$": "PDC.INSTALLED_SCRIPTS"}},
    "PROD":
        {"MSK": {"$INST$": "RBADB", "$TBL$": "PDC.INSTALLED_SCRIPTS"},
         "KRD": {"$INST$": "RBADB", "$TBL$": "PDC.INSTALLED_SCRIPTS_KRD"},
         "NNV": {"$INST$": "RBADB", "$TBL$": "PDC.INSTALLED_SCRIPTS_NNV"},
         "EKB": {"$INST$": "RBADB", "$TBL$": "PDC.INSTALLED_SCRIPTS_EKB"},
         "NSK": {"$INST$": "RBADB", "$TBL$": "PDC.INSTALLED_SCRIPTS_NSK"},
         "SPB": {"$INST$": "RBADB", "$TBL$": "PDC.INSTALLED_SCRIPTS_SPB"}}
}


def isRgnExist(env, rgn):
    return (rgn in db_insts[env])


def getDBUser(env, rgn):
    if len(rgn):
        return db_users[env][rgn]
    return db_users[env]["MSK"]


def getDBDataSource(env, rgn):
    if len(rgn):
        return db_insts[env][rgn]["$INST$"]
    return db_insts[env]["MSK"]["$INST$"]


def getDBTableName(env, rgn):
    if len(rgn):
        return db_insts[env][rgn]["$TBL$"]
    return db_insts[env]["MSK"]["$TBL$"]
