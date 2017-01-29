# coding: cp1251

import os


class Assembly:
    def __init__(self, aDBMgr):
        self.mObj = []
        # self.mUser = Config.db_deploy_user
        # self.mPass = Config.db_deploy_pass
        # self.mWords = ["DROP", "TABLE", "TRIGGER", "FUNCTION", "VIEW", "PROC"]
        self.mDBMgr = aDBMgr

    def createScript(self, aEnv, aInDir, aOutFile, aListFiles):
        objects = {}
        for root, dirs, files in os.walk(aInDir):
            for ddl in files:
                info = os.path.splitext(ddl)
                if info[1] == '.sql':
                    path = os.path.join(root, ddl)
                    obj = self.readScript(path)
                    objects[ddl.upper()] = obj

                    '''
                    self.buildDependencies(obj)
                    self.processFiles(aListFiles)
                    '''

        for sql in aListFiles:
            name, cmd = sql.upper().split(':')
            if name in objects.keys():
                self.processObject(objects[name], cmd)

    def readScript(self, aFile):
        self.mWords = ["DROP", "TABLE", "TRIGGER", "FUNCTION", "VIEW", "PROC", "DEPENDS"]
        obj = {}

        with open(aFile, "rt") as fin:
            for line in fin:
                if line.strip() == "":
                    continue

                for item in self.mWords:
                    strStart = "-- BEGIN " + item
                    strStop = "-- END " + item

                    if line.strip()[:len(strStart)].upper() == strStart:
                        obj[item] = self.readSection(fin, strStop, item == "DEPENDS")
                        self.mWords.remove(item)
                        break
        return obj

    def readSection(self, aFile, aSection, aIsDependency):
        info = []
        for line in aFile:
            if line.strip()[:len(aSection)] == aSection:
                break
            else:
                if not aIsDependency:
                    info.append(line)
                else:
                    if line.strip()[:2] == "--":
                        line = line.strip()[3:].split('.')[1]
                        if line != "":
                            info.append(line)
        return info

    '''
    def buildDependencies(self, aObj):
        for dep in aObj["DEPENDS"]:
                print (dep)

    def processFiles(self, aListFiles):
        for file in aListFiles:
            cmd = file.split(':')[1]
    '''

    def processObject(self, aObj, aCmd):
        print aCmd,
        self.processDrops(aObj, aCmd)

        # TODO
        # ?
        # if depended -> recurse


    def processDrops(self, aObj, aCmd):
        if len(aObj["DROP"]) == 0:
            return

        for drop in aObj["DROP"]:
            drop = drop.strip().upper()

            if drop.endswith(';'):
                drop = drop[:-1]

            bExist = (aCmd == "A")

            tokens = drop.split(" ")

            if tokens[0] == "DROP":
                if tokens[1] == "TABLE":
                    bExist = self.mDBMgr.isTableExist(tokens[2], "T")
                elif tokens[1] == "TRIGGER":
                    bExist = self.mDBMgr.isTriggerExist(tokens[2])
                elif tokens[1] == "VIEW":
                    bExist = self.mDBMgr.isTableExist(tokens[2], "V")
                elif tokens[1] == "INDEX":
                    bExist = self.mDBMgr.isIndexExist(tokens[2])
                elif tokens[1] == "PROCEDURE":
                    name = "".join(tokens[2:]).strip()
                    bExist = self.mDBMgr.isRoutineExist(name, "P")
                elif tokens[1] == "FUNCTION":
                    name = "".join(tokens[2:]).strip()
                    bExist = self.mDBMgr.isRoutineExist(name, "F")
                elif tokens[1] == "SPECIFIC":
                    routine = tokens[2]
                    if routine == "PROCEDURE":
                        bExist = self.mDBMgr.isSpecRoutineExist(tokens[3], "P")
                    elif tokens[1] == "FUNCTION":
                        bExist = self.mDBMgr.isSpecRoutineExist(tokens[3], "F")

            if bExist:
                print drop, "exist"
