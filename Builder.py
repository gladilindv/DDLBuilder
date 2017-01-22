# coding: cp1251

import argparse
import os
import shutil
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
    # название приложения RCI, PDC, FCB, CC, по ним определяются имена сервисных пользователей
    cmdParser.add_argument('App')
    # версия идет в название скриптов
    cmdParser.add_argument('Version')
    # 
    cmdParser.add_argument('-sqlInpPath', default='SQL')
    # 
    cmdParser.add_argument('-sqlOutPath', default='OUT')
    # 
    cmdParser.add_argument('-Rgn', default='')
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
            # пустой файл для того чтобы артефакт в любом случае создался
            os.open(os.path.join(sqlOutPath, "_readme.txt"), os.O_CREAT)
    except IOError as e:
        print ("[ERR] I/O error({0}) : {1} '{2}'".format(e.errno, e.strerror, sqlOutPath))
        quit()

    dbMgr = DataBaseMgr(namespace.Rgn)
    asm = Assembly(namespace.Rgn)

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

        # Создаем папку для временного хранения скриптов
        sqlOutEnvTmpPath = os.path.join(sqlOutEnvPath, "tmp")
        if os.path.exists(sqlOutEnvTmpPath):
            shutil.rmtree(sqlOutEnvTmpPath)
            
        # Копируем все скрипты во временную папку
        shutil.copytree(sqlInpPath, sqlOutEnvTmpPath)
                
        # Заменяем плейсхолдеры, которые находятся в DDL а не в грантах (они в одинарных кавычках)
        # Sources.replacePlaceholdersInFiles(sqlOutEnvTmpPath, env, namespace.Rgn, Config.db_ddl_placeholders)
        
        # Получим список установленных скриптов вместе с md5
        installedSQLScripts = dbMgr.getInstalledSQLScripts(env)
        
        print ("############################################################################")
        print ("### Installed SQL scripts ##################################################")
        pprint.pprint(installedSQLScripts)
        
        # Считаем md5 по всем файлам
        notInstalledSQLScripts = Sources.getNotInstalledSQLScripts(sqlOutEnvTmpPath, installedSQLScripts)

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
            print("      - path:  {0}".format(sqlOutEnvTmpPath))
            print("      - res :  {0}".format(sqlResultScript))
            print("      - args:  {0}".format(sqlArgs))

        else:
            # Запуск Assembly.sql
            # cmdAssembly = "cscript " + namespace.Assembly +
            # " /dbn=" + Config.getDBDataSource(env, namespace.Rgn) +
            # " /dbu=" + Config.db_deploy_user +
            # " /dbp=" + Config.db_deploy_pass +
            # " /i" + sqlOutEnvTmpPath +
            # " /o\"" + sqlResultScript + "\" " +
            # sqlArgs
            #          subprocess.call(cmdAssembly)

            asm.createScript(env, sqlResultScript, notInstalledSQLScripts)

            # Заменяем плейсхолдеры в грантах результирующего скрипта
            Sources.replacePlaceholders(sqlResultScript, env, namespace.Rgn, Config.db_grant_placeholders)

            # Формирование insert-ов
            Sources.addInsertStatements(sqlResultScript, notInstalledSQLScripts, env, namespace.Rgn, namespace.Version)

        # Удаляем папку с временными SQL файлами
        if os.path.exists(sqlOutEnvTmpPath):
            shutil.rmtree(sqlOutEnvTmpPath)
                    
    print ("[INF] End")
