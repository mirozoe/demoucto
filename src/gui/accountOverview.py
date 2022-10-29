import copy
import time
import typing
import re
from PyQt5 import QtCore, QtSql, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter, QDateEdit, QDialog, QGridLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QStatusBar

from gui.widgets.anyCancelWidget import AnyCancel
import utilities.constants as consts
from utilities.inputObjects import AccountList, AccountRecord, AccountStruct, DocumentStruct
from utilities.utilities import getAccounts, getAccountRecord, getDocuments, getTimestamp
from gui.inputDocument import InputDocument
import db.db

# Window constants
IDOC_WIN_TITLE = "Výpis účtu"
DIALOG_WIDTH = 500
COLUMNS = 4

class AccountOverview(QDialog):
    def __init__(self, db: db.db.DBManager, statusBar: QStatusBar) -> None:
        super(AccountOverview, self).__init__()

        self._db = db
        self._accounts = None
        self._statusBar = statusBar

        currentDate = QtCore.QDate.currentDate()
        beginOfMonth = self.prepareBeginOfMonth(currentDate)
        self.readUsedAccounts()

        self._account = self.populateAccountsLineEdit()
        self._beginDate = QDateEdit(beginOfMonth)
        self._currentDate = QDateEdit(currentDate)
        self._table = QTableWidget(self)

        self.setWindowTitle(IDOC_WIN_TITLE)
        self.setMinimumWidth(DIALOG_WIDTH)
        self.setSizeGripEnabled(True)
        self.setModal(True)

        layout = QGridLayout()
        layout.addWidget(QLabel("Vyberte účet"), 0, 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(self._account, 0, 2, 1, 3)
        layout.addWidget(QLabel("Od"), 1, 0, Qt.AlignCenter)
        layout.addWidget(self._beginDate, 1, 1)
        layout.addWidget(QLabel("Do"), 1, 2, Qt.AlignCenter)
        layout.addWidget(self._currentDate, 1, 3)
        layout.addWidget(AnyCancel(consts.BUT_SEARCH, consts.BUT_CANCEL, self.search, self.cancel), 2, 2, 1, 2)
        layout.addWidget(self._table, 3, 0, 1, 4, Qt.AlignCenter) 

        self.setLayout(layout)
        self.exec()


    def cancel(self) -> None:
        self.close()

    def search(self) -> None:
        if self._account.text() == "":
            print("je to prázdné")
            return

        accName, accNo = AccountStruct.parsePresent(self._account.text())
        account = self._getAccountID(accNo)

        documents = self._getDocuments()

        records = self.searchRecords(account)
        self._table.setColumnCount(COLUMNS)
        self._table.setRowCount(len(records))
        self._table.setHorizontalHeaderLabels(["Záznam", "Typ", "MD", "D"])
        for record in records:
            for row in range(0, len(records)):
                self._table.setItem(row, 0, QTableWidgetItem(str(record.id)))
                self._table.setItem(row, 1, QTableWidgetItem(self._translateDocument(record.documenttype, documents)))
                if account == record.debit:
                    self._table.setItem(row, 2, QTableWidgetItem(str(record.price)))
                if account == record.kredit:
                    self._table.setItem(row, 3, QTableWidgetItem(str(record.price)))


    def populateAccountsLineEdit(self) -> QLineEdit:
        """Populates all account types to Insert new Document"""
        accounts = []
        for account in self._accounts.get():
            accounts.append(account.present())
        completer = QCompleter(accounts)
        completer.setFilterMode(Qt.MatchContains)
        edit = QLineEdit()
        edit.setCompleter(completer)
        return edit

    def prepareBeginOfMonth(self, date: QtCore.QDate) -> QtCore.QDate:
        """ Get begining of month date """
        tempDate = copy.deepcopy(date)
        tempDate.setDate(tempDate.year(), tempDate.month(), 1)
        return tempDate
    
    def readUsedAccounts(self) -> None:
        """ Read useful data from DB """
        accountList = AccountList()
        accounts, error = self._db.get("SELECT DISTINCT id,name,no FROM (SELECT debit AS acc FROM accountingdiary UNION SELECT kredit AS acc FROM accountingdiary) AS a INNER JOIN accounts ON a.acc=accounts.id;", getAccounts)
        if not error:
            for account in accounts:
                accountList.append(account)
        self._accounts = accountList

    def searchRecords(self, account) -> typing.List[AccountRecord]:
        recordList = []
        records, error = self._db.get(f"SELECT id,documenttype,debit,kredit,price FROM accountingdiary WHERE date BETWEEN {getTimestamp( self._beginDate.date() )} AND {getTimestamp( self._currentDate.date() )} AND ( debit={account} OR kredit={account} );", getAccountRecord)
        if not error:
            for record in records:
                recordList.append(record)
        else:
            print( error.text() )

        return recordList

    def _getAccountID(self, account: int) -> int:
        accounts, error = self._db.get(f"SELECT id,name,no FROM accounts WHERE no={account}", getAccounts)
        if not error:
            for account in accounts:
                return account.id

        return -1

    def _getDocuments(self) -> typing.List[DocumentStruct]:
        documents, error = self._db.get("SELECT id,name FROM documents", getDocuments)
        if not error:
            return documents

    def _translateDocument(self, no: int, documents: typing.List[DocumentStruct]) -> str:
        for document in documents:
            if document.id == int(no):
                return document.name
        return ""
