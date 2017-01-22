# coding: cp1251

import os
import hashlib

# local
import Config

def replacePlaceholders(path, env, rgn, placeholders):
    """
    Замена плейсхолдеров в файле значениями из конфигурации
    path    - полный путь к файлу
    env     - название среды
    rgn     - название региона
    placeholders - список плейсхолдеров для замены
    """
    with open(path, "rt") as fin:
        fileContent = fin.readlines()
            
    userMap = Config.getDBUser(env, rgn)
    for i, line in enumerate(fileContent):        
        for placeholder in placeholders:
            if placeholder in userMap:
                line = line.replace(placeholder, userMap[placeholder])
                fileContent[i] = line

    with open(path, "wt") as fout:
        fout.writelines(fileContent)

def replacePlaceholdersInFiles(path, env, rgn, placeholders):
    """
    Замена плейсхолдеров в файлах по указанному пути значениями из конфигурации
    path    - папка с файлами
    env     - название среды
    rgn     - название региона
    placeholders - список плейсхолдеров для замены
    """
    for root, dirs, files in os.walk(path):
        for file in files: 
            if os.path.splitext(file)[1] == '.sql':
                filepath = os.path.join(root, file)
                replacePlaceholders(filepath, env, rgn, placeholders)

def getSQLScripts(path):
    """
    Возвращает dict SQL скриптов вместе с hash суммой в указанной папке
    """
    dict = {}
    print("[INF] list of SQL in: {0}".format(path))
    for root, dirs, files in os.walk(path):
        for file in files: 
            if os.path.splitext(file)[1] == '.sql':
                path = os.path.join(root, file)
                hash = hashlib.md5(open(path, 'rb').read()).hexdigest()
                dict[file] = hash

    return dict

def getNotInstalledSQLScripts(path, installedSQLScripts):
    """
    Возвращает список скриптов, которых нет в БД или у которых не совпадает hash
    """
    sqlScriptsForInstall = {}
    allSQLScripts = getSQLScripts(path)
    for sqlScript in allSQLScripts: 
        if sqlScript in installedSQLScripts:
            if installedSQLScripts[sqlScript] == allSQLScripts[sqlScript]:
                continue
            else:                
                sqlScriptsForInstall[sqlScript + ":M"] = allSQLScripts[sqlScript]
        else:
            sqlScriptsForInstall[sqlScript + ":A"] = allSQLScripts[sqlScript]

    return sqlScriptsForInstall

def addInsertStatements(file, sqlScripts, env, rgn, version):
    try:
        fOut = open(file, 'a')
    except IOError as e:
        print ("[ERR] I/O error({0}) : {1} '{2}'".format(e.errno, e.strerror, file))
        return

    fOut.write('\n')
    fOut.write('--*************************************--\n')
    fOut.write('--*************************************--\n')
    fOut.write('\n')

    for script, md5 in sqlScripts.items():
        insert = script.endswith(":A")
        fscriptname = '%-36s' % ("'" + script[:-2] + "'")
        if insert:
            fOut.write("insert into " + Config.getDBTableName(env,
                                                              "") + " (SCRIPT_NAME, SCRIPT_VERSION, SCRIPT_STATUS, SCRIPT_MESSAGE ) values (" + fscriptname + ",'" + version + "',1,'" + md5 + "');\n")
        else:
            fOut.write("update " + Config.getDBTableName(env, "") +
                       " set (SCRIPT_NAME, SCRIPT_VERSION, SCRIPT_STATUS, SCRIPT_MESSAGE ) " + 
                       " = (" + fscriptname +",'" + version + "',1,'" + md5 + "') " +
                       " where SCRIPT_NAME=" + fscriptname.strip() + ";\n")

    fOut.close()
