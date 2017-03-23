# coding: cp1251

import os


class Assembly:
    def __init__(self, aDBMgr):
        self.mWords = []
        self.mDBMgr = aDBMgr

    def createScript(self, aInDir, aOutFile, aListFiles):
        out = {}
        for sql in aListFiles:
            name, cmd = sql.upper().split(':')
            path = os.path.join(aInDir, name)
            if os.path.isfile(path):
                obj = self.readScript(path)
                self.processDrops(obj, cmd)
                out[name] = obj

        # sort objects by dependencies
        dropSQL = "-- drop section\n"
        buildSQL = "-- new section\n"
        for name in out:
            obj = out[name]
            for drop in obj["DROP"]:
                drop = drop.strip().upper()
                if drop:
                    dropSQL += "-- " + name + " \n"
                    dropSQL += drop

            buildSQL += self.buildScript(name, out)

        # serialize objects to aOutFile
        with open(aOutFile, 'w') as f:
            f.write('-- SQL ASSEMBLY FILE --\n\n')
            f.write(dropSQL)
            f.write('\n\n')
            f.write(buildSQL)

    def buildScript(self, aName, aObjects):
        sql = ""
        sections = ["TABLE", "TRIGGER", "FUNCTION", "VIEW", "PROC"]
        obj = aObjects[aName]
        # if already used return
        if "OK" in obj and obj["OK"]:
            return ""
        for dep in obj["DEPENDS"]:
            name = dep + ".SQL"
            if name in aObjects:
                sql += self.buildScript(name, aObjects)

        sql += "\n\n-- " + aName + "\n"
        for item in sections:
            if item in obj:
                for row in obj[item]:
                    sql += row
                    obj["OK"] = True
        return sql

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

    def processDrops(self, aObj, aCmd):
        if len(aObj["DROP"]) == 0:
            return

        for num, drop in enumerate(aObj["DROP"]):
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

            # if not exist -> mark as don`t drop
            if not bExist:
                aObj["DROP"][num] = ""
