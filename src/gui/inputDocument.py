from datetime import date, datetime
from PyQt5 import QtSql
from PyQt5.QtCore import QDate, QLine, Qt
from PyQt5.QtWidgets import QCompleter, QDateEdit, QDialog, QGridLayout, QHBoxLayout, QLineEdit, QMainWindow, QMenuBar, QLabel, QMessageBox, QPushButton, QStatusBar,  QVBoxLayout, QWidget
import typing
import time

import db.db
from gui.widgets.anyCancelWidget import AnyCancel
from gui.widgets.messageBox import MessageBox
from utilities.accountingDiaryObjects import AccountingDiaryObject
import utilities.utilities as utils
import utilities.constants as consts
import utilities.inputObjects as obj

# Window constants
IDOC_WIN_TITLE = "Vložte účetní doklad"

class InputDocument(QDialog):
    """Dialog window for inserting accounting document"""

    def __init__(self, db: db.db.DBManager, accounts: typing.List[obj.AccountStruct], documents: typing.List[obj.DocumentStruct], statusBar: QStatusBar, preFill: obj.InputDocumentStruct=None, parent=None) -> None:
        super(InputDocument, self).__init__(parent)
        self._db = db
        self._accounts = accounts
        self._documents = documents
        self._statusBar = statusBar
        self._preFill = preFill

        self.setWindowTitle(IDOC_WIN_TITLE)
        self.setModal(True)

        vLayout = QVBoxLayout()
        vLayout.addWidget(self.inputGrid())
        vLayout.addStretch()
        vLayout.addWidget(AnyCancel(consts.BUT_SAVE, consts.BUT_CANCEL, self.save, self.cancel))

        self.setLayout(vLayout)
        self.exec()
    
    def inputGrid(self) -> QWidget:
        """Draws widgets into grid"""
        self._docType = self.populateDocumentsLineEdit()
        self._debit = self.populateAccountsLineEdit()
        self._kredit = self.populateAccountsLineEdit()
        self._docNo = self.populateDocNo()
        self._docNo.setDisabled(True)
        self._docDate = QDateEdit(utils.currentQDate())
        self._docDate.dateChanged.connect(self.updateDocNo)
        self._price = QLineEdit()
        self._notice = QLineEdit()

        if self._preFill != None:
            self._docType.setText(self._documents.searchById(self._preFill.document)[0].name)
            self._debit.setText(self._accounts.searchById(self._preFill.debit)[0].no)
            self._kredit.setText(self._accounts.searchById(self._preFill.kredit)[0].no)
            self._docDate.setDate(date.fromtimestamp(self._preFill.date))
            self._docDate.setDisabled(True)
            self._price.setText(self._preFill.price)
            self._notice.setText(self._preFill.notice)
            self._docNo = self.populateDocNo(self._preFill.id)
            self._docNo.setDisabled(True)

        widget = QWidget()
        grid = QGridLayout()
        grid.addWidget(QLabel("Číslo dokladu"), 0, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(QLabel("Datum uskutečnění"), 0, 2)
        grid.addWidget(self._docNo, 1, 0, 1, 2)
        grid.addWidget(self._docDate, 1, 2)
        grid.addWidget(QLabel("Typ dokladu"), 2, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(QLabel("Cena"), 2, 2, Qt.AlignCenter)
        grid.addWidget(self._docType, 3, 0, 1, 2)
        grid.addWidget(self._price, 3, 2)

        grid.addWidget(QLabel("MD"), 4, 1, Qt.AlignCenter)
        grid.addWidget(QLabel("D"), 4, 2, Qt.AlignCenter)
        grid.addWidget(QLabel("Účty"), 5, 0)
        grid.addWidget(self._debit, 5, 1)
        grid.addWidget(self._kredit, 5, 2)
        
        grid.addWidget(QLabel("Poznámka"), 6, 0)
        grid.addWidget(self._notice, 6, 1, 1, 2)

        widget.setLayout(grid)
        return widget

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

    def populateDocumentsLineEdit(self) -> QLineEdit:
        """Populates all document types to Insert new Document"""
        documents = []
        for document in self._documents.get():
            documents.append(document.name)
        completer = QCompleter(documents)
        completer.setFilterMode(Qt.MatchContains)
        edit = QLineEdit()
        edit.setCompleter(completer)
        return edit

    def populateDocNo(self, id = None) -> QLineEdit:
        """Populates DocumentId field, initialy with current date, otherweise respective to selected date.
            It also asks database to get next available id (last two digits)
        """
        docNo = QLineEdit()
        if id != None:
            docNo.setText(id)
        else:
            docNo.setText(str(self._db.getNextDocuId(utils.transformDateToDocuIdPrefix(utils.currentQDate()))))
        docNo.setReadOnly(True)
        return docNo

    def updateDocNo(self) -> None:
        """Update DocumentId that it corresponds with selected date"""
        return self._docNo.setText(str(self._db.getNextDocuId(utils.transformDateToDocuIdPrefix(self._docDate.date()))))

    def save(self) -> None:
        """Save callback used for saving document into DB"""
        inputDocu = obj.InputDocumentStruct( self._docNo.text(), self._docType.text(), self._debit.text(), self._kredit.text(), self._price.text(), self._notice.text(), str(time.time()) )
        errors = inputDocu.validate(self._documents, self._accounts)
        if len(errors) > 0:
            text = 'Nastala následující chyba:\n{}'.format("\n".join(errors))
            if len(errors) > 1:
                text = 'Nastaly následující chyby:\n{}'.format("\n".join(errors))
            MessageBox(QMessageBox.Critical, text)
            return

        docId, doc, deb, kre, pri, notice, date = inputDocu.get()
        if self._preFill == None:
            error = self._db.put(f'INSERT INTO accountingdiary VALUES ({int(docId)}, "{doc}", "{deb}", "{kre}", "{pri}", "{notice}", {date})', self.getAll)
            if error:
                print(f'Error writing into accountingdiary: {error.text()}\nINSERT INTO accountingdiary VALUES ({docId}, {doc}, {deb}, {kre}, {pri}, {notice}, {date})')
                MessageBox(QMessageBox.Critical, f"Nastala chyba při ukládání dokumentu: {error.text()}")
                return
        else:
            error = self._db.put(f'UPDATE accountingdiary SET documenttype="{doc}",debit="{deb}",kredit="{kre}",price={pri},notice="{notice}", date={date} WHERE id={docId}', self.getAll)
            if error:
                print(f'Error updating accountingdiary: {error.text()}\nUPDATE accountingdiary SET documenttype="{doc}",debit="{deb}",kredit="{kre}",price={pri},notice="{notice}", date={date} WHERE id={docId}')
                MessageBox(QMessageBox.Critical, f"Nastala chyba při ukládání dokumentu: {error.text()}")
                return
        self._statusBar.showMessage("Dokument byl uložen", 5000)
        self.close()

    def cancel(self) -> None:
        """Cancel callback to discard all changes"""
        self.close()

    def getAll(self, q: QtSql.QSqlQuery) -> None:
        print(f'response from write {q.result()}')