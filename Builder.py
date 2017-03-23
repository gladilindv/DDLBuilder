# coding: cp1251

import argparse
import os
import datetime
import pprint

# local
from Helpers import DataBaseMgr
from Assembly import Assembly
import Sources
import Config


# ������ ����
envs = ["AA", "CC", "PROD"]

# ������� � �������� �����
sqlInpPath = "SQL"
sqlOutPath = "OUT"

##########################################################################################
# ������ ��������� ������
def createParser ():
    cmdParser = argparse.ArgumentParser()
    # ������ ���� � �������� ��������
    cmdParser.add_argument('Version')
    # 
    cmdParser.add_argument('-sqlInpPath', default='SQL')
    # 
    cmdParser.add_argument('-sqlOutPath', default='OUT')
    # 
    cmdParser.add_argument('-Rgn', default='MSK')
    # 
    cmdParser.add_argument('-Env', default='AA,CC,PROD')
    #
    cmdParser.add_argument('-Assembly', default='Assembly.vbs')

    return cmdParser

##########################################################################################
# ������ �������
if __name__ == '__main__':

    print ("############################################################################")
    print ("### Building SQL scripts ###################################################")
    print ("############################################################################")
  
    # ������ ���������� ������
    parser = createParser()
    namespace = parser.parse_args()

    # ������� ���� ��������� �� �����
    print ("[INF] version {0}".format(namespace.Version))
    
    sqlOutPath = namespace.sqlOutPath
    sqlInpPath = namespace.sqlInpPath
    envs = namespace.Env.split(",")

    if not os.path.exists(sqlInpPath):
        print ("[ERR] Input path is not exist: {0}".format(sqlInpPath))
        os.makedirs(sqlInpPath)
        quit()

    # ������� ����� ��� SQL �������� ��� ������
    print ("[INF] creating folder {0}".format(sqlOutPath))
    
    try:
        if not os.path.exists(sqlOutPath):
            os.makedirs(sqlOutPath)

        rpath = os.path.join(sqlOutPath, "_readme.txt")
        with open(rpath, 'wt') as f:
            f.write("Started at: {0}\n".format(datetime.datetime.now()))
    except IOError as e:
        print ("[ERR] I/O error({0}) : {1} '{2}'".format(e.errno, e.strerror, sqlOutPath))
        quit()

    dbMgr = DataBaseMgr(namespace.Rgn)
    asm = Assembly(dbMgr)

    for env in envs:
        print ("[INF] ENV {0}".format(env))
        
        # ������ �� ��� ������ ���� ������ ������� ������� ��� ����� ������� ���
        if len(namespace.Rgn) > 0 and not Config.isRgnExist(env, namespace.Rgn):
            print ("[INF] Rgn {0} does not exist in Env {1}".format(namespace.Rgn, env))
            continue
        
        # ������� ����� ��� ����� ��� ������� �������� �������
        sqlOutEnvPath = os.path.join(sqlOutPath, env)
        if not os.path.exists(sqlOutEnvPath):
            os.mkdir(sqlOutEnvPath)

        # ������� ����� ��� �������
        sqlOutEnvRgnPath = os.path.join(sqlOutEnvPath, namespace.Rgn)
        if not os.path.exists(sqlOutEnvRgnPath):
            os.mkdir(sqlOutEnvRgnPath)

        # �������� ������������, ������� ��������� � DDL � �� � ������� (��� � ��������� ��������)
        # Sources.replacePlaceholdersInFiles(sqlOutEnvTmpPath, env, namespace.Rgn, Config.db_ddl_placeholders)

        # ���������� � �� (������� �����). ��� �������� � ��������� ����� - �������������
        if not dbMgr.connect(env):
            with open(rpath, 'a') as f:
                err = ",".join(dbMgr.mErr.splitlines())
                f.write("Connection error: \n\tRgn: {0}\n\tEnv: {1}\n\tErr: {2}\n\n".format(namespace.Rgn, env, err))
            continue

        # ������� ������ ������������� �������� ������ � md5
        installedSQLScripts = dbMgr.getInstalledSQLScripts()
        
        print ("############################################################################")
        print ("### Installed SQL scripts ##################################################")
        pprint.pprint(installedSQLScripts)
        
        # ������� md5 �� ���� ������
        notInstalledSQLScripts = Sources.getNotInstalledSQLScripts(sqlInpPath, installedSQLScripts)

        print ("############################################################################")
        print ("### Not installed SQL scripts ##############################################")
        pprint.pprint(notInstalledSQLScripts)

        # ����� assembly.vbs
        sqlResultScript = os.path.join(sqlOutEnvRgnPath, "pdc_" + namespace.Version + ".sql")
        sqlArgs = " ".join(notInstalledSQLScripts).replace(".sql", "")

        if not notInstalledSQLScripts:
            print("[INF] Nothing to install")            
            
        elif not sqlResultScript or not sqlArgs:
            print("[ERR] Wrong input parameters for Assembly.vbs")
            print("      - path:  {0}".format(sqlInpPath))
            print("      - res :  {0}".format(sqlResultScript))
            print("      - args:  {0}".format(sqlArgs))

        else:
            asm.createScript(sqlInpPath, sqlResultScript, notInstalledSQLScripts)

            if os.path.isfile(sqlResultScript):
                # �������� ������������ � ������� ��������������� �������
                Sources.replacePlaceholders(sqlResultScript, env, namespace.Rgn, Config.db_grant_placeholders)

                # ������������ insert-��
                Sources.addInsertStatements(sqlResultScript, notInstalledSQLScripts, env, namespace.Rgn, namespace.Version)

        dbMgr.disconnect()
                    
    print ("[INF] End")
    with open(rpath, 'a') as f:
        f.write("Finished at: {0}\n".format(datetime.datetime.now()))
