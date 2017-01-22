# coding: cp1251

import os
import Config

class Assembly:
    def __init__(self, aHostWarnIsOn=False):
        self.mObj = []
        self.mUser = Config.db_deploy_user
        self.mPass = Config.db_deploy_pass
        # self.mWords = ["DROP", "TABLE", "TRIGGER", "FUNCTION", "VIEW", "PROC"]

    def createScript(self, aEnv, aInDir, aOutFile, aListFiles):
        for root, dirs, files in os.walk(aInDir):
            for file in files:
                info = os.path.splitext(file)
                if info[1] == '.sql':
                    filepath = os.path.join(root, file)
                    self.readScript(filepath)

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
        print (obj)

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
                        line = line.split('.')[0][3:]

                        if line != "":
                            info.append(line)
        return info

