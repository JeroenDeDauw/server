#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Copyright (c) 2014 Gael Honorez.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#-------------------------------------------------------------------------------


from logging import handlers

from PySide.QtCore import QObject

from passwords import DB_SERVER, DB_PORT, DB_LOGIN, DB_PASSWORD, DB_TABLE
import config
from config import Config

#update server
from updater.updateServer import *

UNIT16 = 8

class start(QObject):

    def __init__(self, parent=None):
        try :
            super(start, self).__init__(parent)
            self.rootlogger = logging.getLogger("")
            self.logHandler = handlers.RotatingFileHandler(config.LOG_PATH + "serverUpdater.log", backupCount=15, maxBytes=524288 )
            self.logFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-20s %(message)s')
            self.logHandler.setFormatter(self.logFormatter)
            self.rootlogger.addHandler(self.logHandler)
            self.rootlogger.setLevel(eval("logging." + Config['serverUpdater']['loglevel']))
            self.logger = logging.getLogger(__name__)

            self.logger.info("Update server starting")
            self.db = QtSql.QSqlDatabase("QMYSQL")
            self.db.setHostName(DB_SERVER)
            self.db.setPort(DB_PORT)

            self.db.setDatabaseName(DB_TABLE)
            self.db.setUserName(DB_LOGIN)
            self.db.setPassword(DB_PASSWORD)
            self.db.setConnectOptions("MYSQL_OPT_RECONNECT=1")

            if not self.db.open():
                self.logger.error(self.db.lastError().text())

            else:
                self.logger.info("DB opened.")

            self.updater = updateServer(self)
            if not self.updater.listen(QtNetwork.QHostAddress.Any, 9001):

                self.logger.error("Unable to start the server")

                return
            else:
                self.logger.info("Starting the update server on  %s:%i" % (self.updater.serverAddress().toString(),self.updater.serverPort()))
        except Exception as e:
            self.logger.exception("Error: %r" % e)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    import sys

    try:

        app = QtCore.QCoreApplication(sys.argv)
        server = start()
        app.exec_()

    except Exception as e:

        logger.exception("Error: %r" % e)
        logger.debug("Finishing main")

