from PyQt5 import QtSql
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QHBoxLayout, QMainWindow, QMenuBar, QLabel, QPushButton, QVBoxLayout, QWidget
import typing

from gui.accountingDiary import AccountingDiary
from gui.accountOverview import AccountOverview
from gui.inputDocument import InputDocument
from utilities.inputObjects import AccountList, AccountStruct, DocumentList, DocumentStruct
from utilities.utilities import getAccounts
import db.db

# Window constants
WIN_TITLE = "Demo účto"
WIN_WIDTH = 800
WIN_HEIGHT = 500

CENTRAL_LABEL_TEXT = "Hotelová škola, Obchodní akademie a Střední průmyslová škola, Teplice, Benešovo náměstí 1, p.o., Teplice"

class MainWindow (QMainWindow):
    """Main application window"""

    def __init__(self, db: db.db.DBManager, parent=None) -> None:
        super(MainWindow, self).__init__(parent)
        self._db = db
        self.readPredefinedAccounts()                       # read all accounts from DB
        self.readPredefinedDocuments()                      # read all document types from DB

        self.setGeometry(0, 0, WIN_WIDTH, WIN_HEIGHT)       # main window
        self.setWindowTitle(WIN_TITLE)                      # main window title

        menuBar = self.menuBar()                            # create menu bar
        self.populateMenuBar(menuBar)
        
        centralWidget = QWidget()                           # create central text widget
        hLayout = QHBoxLayout()
        hLayout.addStretch()
        label = QLabel(CENTRAL_LABEL_TEXT, self)
        hLayout.addWidget(label)
        hLayout.addStretch()
        centralWidget.setLayout(hLayout)
        self.setCentralWidget(centralWidget)

    def populateMenuBar(self, menuBar: QMenuBar) -> None:
        """Fill menuBar Soubor, Doklad and Přehled """
        
        file = menuBar.addMenu("Soubor")

        close = QAction("&Konec", self)
        close.triggered.connect(self.quit)
        close.setShortcut(QKeySequence.Quit)
        file.addAction(close)

        invoice = menuBar.addMenu("Doklady")

        inputDoc = QAction("&Nový doklad", self)
        inputDoc.triggered.connect(self.inputInvoice)
        inputDoc.setShortcut(QKeySequence.New)
        invoice.addAction(inputDoc)

        overview = menuBar.addMenu("Přehled")

        accBook = QAction("Účetní deník", self)
        accBook.triggered.connect(self.accountingDiaryView)
        accBook.setShortcut(QKeySequence.Open)
        overview.addAction(accBook)

        accountOver = QAction("Přehled účtu", self)
        accountOver.triggered.connect(self.accountOverView)
        overview.addAction(accountOver)

    def inputInvoice(self) -> None:
        """Opens input accounting document dialog"""
        InputDocument(self._db, self._accounts, self._documents, self.statusBar())

    def accountingDiaryView(self) -> None:
        """Opens accounting diary with overview of documents"""
        AccountingDiary(self._db, self._accounts, self._documents, self.statusBar())

    def accountOverView(self) -> None:
        """Opens overview for one account"""
        AccountOverview(self._db, self.statusBar())

    def quit(self):
        """Quits from application"""
        self._db.close()
        self.close()


    # Read useful data from DB
    def readPredefinedAccounts(self) -> None:
        accounts = AccountList()
        rawAccount, error = self._db.get("SELECT * FROM accounts ORDER BY name", getAccounts)
        if not error:
            for account in rawAccount:
                accounts.append(account)
        self._accounts = accounts

    def readPredefinedDocuments(self) -> None:
        documents = DocumentList()
        rawDocuments, error = self._db.get("SELECT * FROM documents ORDER BY name", self.getDocuments)
        if not error:
            for document in rawDocuments:
                documents.append(document)
        self._documents = documents

    def getDocuments(self, q: QtSql.QSqlQuery) -> typing.List[DocumentStruct]:
        """Extract documents from query"""
        list = []
        while q.next():
            doc = DocumentStruct( str(q.value(0)), q.value(1) )
            list.append(doc)
        return list
