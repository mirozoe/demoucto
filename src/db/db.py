import os
import typing
from PyQt5 import QtSql
import utilities.constants as consts

class DBManager:
    """Class is responsible for actions above SQLite DB"""

    def __init__(self, database: str):
        self._db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self._db.setDatabaseName(database)
        if not self._db.open():
            print("DB is not opened")
            os._exit(consts.DB_IS_NOT_OPENED)

    def get(self, queryString: str, callback: typing.Callable) -> tuple:
        """ Get data from DB
            returns tuple (QtSql.QSqlQuery, QtSql.QSqlError)
        """
        query = QtSql.QSqlQuery()
        if query.exec(queryString):
            return callback(query), None

        return None, query.lastError()

    def getNextDocuId(self, prefix: str) -> int:
        """Get next available DocumentId"""
        query = QtSql.QSqlQuery()
        if query.exec(f"SELECT id FROM accountingdiary WHERE id LIKE '{prefix}%' ORDER BY id DESC LIMIT 1"):
            i = 0
            while query.next():
                no = str(query.value(0))[-2:]
                number = int(no) + 1
                i += 1
                return int(f"{prefix}{str(number).rjust(2, '0')}")
            if i == 0:
                return f"{prefix}01"
        return 0

    def put(self, queryString: str, callback: typing.Callable) -> str:
        """ Put data into DB
            returns QtSql.QSqlError
        """
        response, error = self.get(queryString, callback)
        return error

    def delete(self, queryString: str, callback: typing.Callable) -> str:
        ''' Delete data from DB
            returns QtSql.QSqlError
        '''
        response, error = self.get(queryString, callback)
        return error

    def close(self):
        """Function responsible for closing DB"""
        self._db.close()
