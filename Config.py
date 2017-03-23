# coding: cp1251

db_deploy_user = "srv-ps-builder"
db_deploy_pass = "C,jhjxysqRjydtqth"

db_ddl_placeholders = ["'$RCI_SRV_USER$'"]
db_grant_placeholders = ["$DB2_USER_NAME$", "$PDC_SUPPORT_GROUP$", "$PDC_SERVICE_GROUP$"]

db_users = {
    "default": {
        "$DB2_USER_NAME$": "SRV_TST_PDC",
        "$PDC_SUPPORT_GROUP$": "SEC-IT AS ADMINS-RUR BO",
        "$PDC_SERVICE_GROUP$": "APP-PDCSERVICEACCOUNTS"
    },
    "PROD": {
        "MSK": {"$DB2_USER_NAME$": "SRV_PDC"},
        "KRD": {"$DB2_USER_NAME$": "SRV_PDC"},
        "NNV": {"$DB2_USER_NAME$": "SRV_PDC"},
        "EKB": {"$DB2_USER_NAME$": "SRV_PDC"},
        "NSK": {"$DB2_USER_NAME$": "SRV_PDC"},
        "SPB": {"$DB2_USER_NAME$": "SRV_PDC"}
    }
}

db_host = {
    "AA": "s-msk-v-db2aa",
    "CC": "s-msk-t-db2cc",
    "DD": "s-msk-d-db2dd",
    "PROD": "s-msk-p-db2"
}

db_insts = {
    "default": {
        "$INST$": "RBADB",
        "$TBL$": "PDC.INSTALLED_SCRIPTS"
    },
    "AA": {
        "MSK": {"$INST$": "RBAPRV01"},
        "KRD": {"$INST$": "KRDDB_A2"}},
    "CC": {
        "MSK": {"$INST$": "RBATST02"},
        "KRD": {"$INST$": "KRDDB_CP"}},
    "DD": {
        "MSK": {"$INST$": "RBADBTS1"},
        "KRD": {"$INST$": "KRDDB_D2"}},
    "PROD": {
        "MSK": {},
        "KRD": {"$TBL$": "PDC.INSTALLED_SCRIPTS_KRD"},
        "NNV": {"$TBL$": "PDC.INSTALLED_SCRIPTS_NNV"},
        "EKB": {"$TBL$": "PDC.INSTALLED_SCRIPTS_EKB"},
        "NSK": {"$TBL$": "PDC.INSTALLED_SCRIPTS_NSK"},
        "SPB": {"$TBL$": "PDC.INSTALLED_SCRIPTS_SPB"}}
}


def isRgnExist(env, rgn):
    return rgn in db_insts[env]


def getDBUser(env, rgn):
    usr = db_users["default"]
    if env in db_users and rgn in db_users[env]:
        for item in db_grant_placeholders:
            if item in db_users[env][rgn]:
                usr[item] = db_users[env][rgn][item]
    return usr


def getDBDataSource(env, rgn):
    ds = db_insts["default"]["$INST$"]
    if env in db_insts and rgn in db_insts[env] and "$INST$" in db_insts[env][rgn]:
        ds = db_insts[env][rgn]["$INST$"]
    return ds


def getDBTableName(env, rgn):
    tb = db_insts["default"]["$TBL$"]
    if env in db_insts and rgn in db_insts[env] and "$TBL$" in db_insts[env][rgn]:
        tb = db_insts[env][rgn]["$TBL$"]
    return tb
