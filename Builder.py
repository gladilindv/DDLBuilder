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


# Список сред
envs = ["AA", "CC", "PROD"]

# Входная и выходная папка
sqlInpPath = "SQL"
sqlOutPath = "OUT"

##########################################################################################
# парсер командной строки
def createParser ():
    cmdParser = argparse.ArgumentParser()
    # версия идет в название скриптов
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
# Начало скрипта
if __name__ == '__main__':

    print ("############################################################################")
    print ("### Building SQL scripts ###################################################")
    print ("############################################################################")
  
    # парсим коммандную строку
    parser = createParser()
    namespace = parser.parse_args()

    # выводим наши параметры на экран
    print ("[INF] version {0}".format(namespace.Version))
    
    sqlOutPath = namespace.sqlOutPath
    sqlInpPath = namespace.sqlInpPath
    envs = namespace.Env.split(",")

    if not os.path.exists(sqlInpPath):
        print ("[ERR] Input path is not exist: {0}".format(sqlInpPath))
        os.makedirs(sqlInpPath)
        quit()

    # Создаем папку для SQL скриптов для сборки
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
        
        # Защита на тот случай если просят создать скрипты для среды которой нет
        if len(namespace.Rgn) > 0 and not Config.isRgnExist(env, namespace.Rgn):
            print ("[INF] Rgn {0} does not exist in Env {1}".format(namespace.Rgn, env))
            continue
        
        # Создаем папку для среды для которой собираем скрипты
        sqlOutEnvPath = os.path.join(sqlOutPath, env)
        if not os.path.exists(sqlOutEnvPath):
            os.mkdir(sqlOutEnvPath)

        # Создаем папку для региона
        sqlOutEnvRgnPath = os.path.join(sqlOutEnvPath, namespace.Rgn)
        if not os.path.exists(sqlOutEnvRgnPath):
            os.mkdir(sqlOutEnvRgnPath)

        # Заменяем плейсхолдеры, которые находятся в DDL а не в грантах (они в одинарных кавычках)
        # Sources.replacePlaceholdersInFiles(sqlOutEnvTmpPath, env, namespace.Rgn, Config.db_ddl_placeholders)

        # Соединение с БД (текущая среда). При переходе к следующей среде - отсоединяться
        if not dbMgr.connect(env):
            with open(rpath, 'a') as f:
                err = ",".join(dbMgr.mErr.splitlines())
                f.write("Connection error: \n\tRgn: {0}\n\tEnv: {1}\n\tErr: {2}\n\n".format(namespace.Rgn, env, err))
            continue

        # Получим список установленных скриптов вместе с md5
        installedSQLScripts = dbMgr.getInstalledSQLScripts()
        
        print ("############################################################################")
        print ("### Installed SQL scripts ##################################################")
        pprint.pprint(installedSQLScripts)
        
        # Считаем md5 по всем файлам
        notInstalledSQLScripts = Sources.getNotInstalledSQLScripts(sqlInpPath, installedSQLScripts)

        print ("############################################################################")
        print ("### Not installed SQL scripts ##############################################")
        pprint.pprint(notInstalledSQLScripts)

        # Вызов assembly.vbs
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
                # Заменяем плейсхолдеры в грантах результирующего скрипта
                Sources.replacePlaceholders(sqlResultScript, env, namespace.Rgn, Config.db_grant_placeholders)

                # Формирование insert-ов
                Sources.addInsertStatements(sqlResultScript, notInstalledSQLScripts, env, namespace.Rgn, namespace.Version)

        dbMgr.disconnect()
                    
    print ("[INF] End")
    with open(rpath, 'a') as f:
        f.write("Finished at: {0}\n".format(datetime.datetime.now()))
