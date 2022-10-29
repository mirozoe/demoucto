import time
import typing
from PyQt5 import QtSql
from PyQt5 import QtCore
from PyQt5.QtCore import QDate
from utilities.inputObjects import AccountStruct, AccountRecord, DocumentStruct
import datetime

def currentQDate() -> QtCore.QDate:
    """Gets current date and returns QDate"""
    t = datetime.date.today()
    return QtCore.QDate(t.year, t.month, t.day)

def transformDateToDocuIdPrefix(d: QtCore.QDate) -> str:
    """Transforms QDate to string aka DocumentID prefix"""
    m = d.month()
    day = d.day()
    return f"{d.year()}{str(m).rjust(2, '0')}{str(day).rjust(2, '0')}"

def getTimestamp(date: QtCore.QDate) -> int:
    print(type(date))
    return int( time.mktime( date.toPyDate().timetuple() ) ) 

def getAccounts(q: QtSql.QSqlQuery) -> typing.List[AccountStruct]:
    """Extract accounts from query"""
    list = []
    while q.next():
        account = AccountStruct( str(q.value(0)), q.value(1), q.value(2) )
        list.append(account)
    return list

def getAccountRecord(q: QtSql.QSqlQuery) -> typing.List[AccountRecord]:
    """Extract account records for one account"""
    list = []
    while q.next():
        record = AccountRecord( q.value(0), q.value(1), q.value(2), q.value(3), q.value(4) )
        list.append(record)
    return list

def getDocuments(q: QtSql.QSqlQuery) -> typing.List[DocumentStruct]:
    """Extract documents"""
    list = []
    while q.next():
        document = DocumentStruct( q.value(0), q.value(1) )
        list.append(document)
    return list
