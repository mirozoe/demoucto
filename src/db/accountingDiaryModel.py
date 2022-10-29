from PyQt5 import QtCore, QtSql
import typing

import db.db
from utilities.accountingDiaryObjects import AccountingDiaryObject

class AccountingDiaryModel(QtCore.QAbstractTableModel):

    def __init__(self, db: db.db.DBManager) -> None:
        super(AccountingDiaryModel, self).__init__()
        self._db = db
        self._headers = ["Číslo dokladu", "Cena", "Dokument", "MD", "D", "Poznámka", "Datum"]

        query = "SELECT a.id,a.documenttype,documents.name,a.debit,a.debitno,a.kredit,accounts.no AS kredit,a.price,a.notice,a.date FROM \
            (SELECT accountingdiary.id,documenttype,debit,accounts.no AS debitno,kredit,price,notice,date FROM \
                accountingdiary INNER JOIN accounts ON accountingdiary.debit=accounts.id) AS a \
                INNER JOIN accounts ON a.kredit=accounts.id \
                INNER JOIN documents ON documents.id=a.documenttype"
        self._documents, error = db.get(query, self.parseQueryResponse)
        if error:
            print("Cannot read accounting diary")

    def data(self, index: QtCore.QModelIndex(), role: QtCore.Qt.DisplayRole) -> typing.Any:
        if not index.isValid():
           return None

        if not 0 <= index.row() < len(self._documents):
            return None

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return self._documents[index.row()].id
            elif index.column() == 1:
                return self._documents[index.row()].price
            elif index.column() == 2:
                return self._documents[index.row()].docTypeName
            elif index.column() == 3:
                return self._documents[index.row()].debit
            elif index.column() == 4:
                return self._documents[index.row()].kredit
            elif index.column() == 5:
                return self._documents[index.row()].notice
            elif index.column() == 6:
                return self._documents[index.row()].date
            
        return None

    def update(self) -> None:
        return self.__init__(self._db)

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Horizontal:
            return QtCore.QVariant()
        # What's the header for the given column?
        return self._headers[section]

    def columnCount(self, parent: QtCore.QModelIndex()) -> int:
        return AccountingDiaryObject.columns

    def rowCount(self, parent: QtCore.QModelIndex()) -> int:
        return len(self._documents)

    def row(self, index: int) -> AccountingDiaryObject:
        return self._documents[index]

    def parseQueryResponse(self, q: QtSql.QSqlQuery) -> typing.List[AccountingDiaryObject]:
        list = []
        while q.next():
            document = AccountingDiaryObject( q.value(0), q.value(1), q.value(2), q.value(3), q.value(4), q.value(5), q.value(6), q.value(7), q.value(8), q.value(9) )
            list.append(document)
        return list
