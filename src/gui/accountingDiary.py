import typing
from PyQt5 import QtCore, QtSql, QtGui, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QTableView, QStatusBar, QVBoxLayout

from gui.widgets.anyCancelWidget import AnyCancel
import utilities.constants as consts
import db.db
import db.accountingDiaryModel
from utilities.inputObjects import AccountStruct, DocumentStruct
from gui.inputDocument import InputDocument

# Window constants
IDOC_WIN_TITLE = "Účetní deník"
DIALOG_WIDTH = 500

class AccountingDiary(QDialog):
    def __init__(self, db: db.db.DBManager, accounts: typing.List[AccountStruct], documents: typing.List[DocumentStruct], statusBar: QStatusBar) -> None:
        super(AccountingDiary, self).__init__()

        self._db = db
        self._accounts = accounts
        self._documents = documents
        self._statusBar = statusBar
        self._selectedRow: QtCore.QModelIndex = None

        self.setWindowTitle(IDOC_WIN_TITLE)
        self.setMinimumWidth(DIALOG_WIDTH)
        self.setSizeGripEnabled(True)
        self.setModal(True)

        vLayout = QVBoxLayout()
        vLayout.addWidget(QLabel("Pro editaci, klikněte dvakrát na řádek tabulky"))
        vLayout.addWidget(self.table())
        vLayout.addStretch()
        vLayout.addWidget(AnyCancel(consts.BUT_DEL, consts.BUT_CANCEL, self.delete, self.cancel))

        self.setLayout(vLayout)
        self.exec()

    def table(self) -> QTableView:
        ''' Table with all records needs to be filled '''
        self._model = db.accountingDiaryModel.AccountingDiaryModel(self._db)
        view = QTableView()
        view.setModel(self._model)
        view.clicked.connect(self.selectRow)
        view.doubleClicked.connect(self.updateRow)
        return view

    def selectRow(self, tableRow: QtCore.QModelIndex) -> None:
        ''' Single click on table updates selectedRow '''
        self._selectedRow = tableRow

    def updateRow(self, tableRow: QtCore.QModelIndex) -> None:
        ''' Double click on table line cause to open input dialog and edit content'''
        print(f"Row {self._model.row(tableRow.row()).kredit}")
        InputDocument(self._db, self._accounts, self._documents, self._statusBar, self._model.row(tableRow.row()).toInputDocumentStruct())
        # update model
        self._model.update()
        self._model.dataChanged.emit(tableRow, tableRow)

    def delete(self) -> None:
        ''' Delete button functionality '''
        if self._selectedRow != None:
            id = self._model.row(self._selectedRow.row()).id
            error = self._db.delete(f"DELETE FROM accountingdiary WHERE id={id}", self.deleteCallback)
            if error:
                print(f"Error deleting record from accountingdiary with id: {id}: {error}")
                return
            self._model.update()
            self._model.dataChanged.emit(self._selectedRow, self._selectedRow)
            self._statusBar.showMessage("Záznam byl smazán", 5000)

    def cancel(self) -> None:
        self.close()

    def deleteCallback(self, query: QtSql.QSqlQuery) -> None:
        pass