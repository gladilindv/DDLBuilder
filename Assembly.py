# coding: cp1251

import Config

class Assembly:
    def __init__(self, aHostWarnIsOn=False):
        self.mObj = []
        self.mUser = Config.db_deploy_user
        self.mPass = Config.db_deploy_pass

    def createScript(self, aEnv, aOutFile, aListFiles):
        for file in aListFiles:
            file

