from PyQt5 import QtSql
from PyQt5.QtWidgets import QApplication
import gui.mainWindow
import db.db

# Constants
DATABASE = "data/accounting.db"

def callback(row: QtSql.QSqlQuery) -> str:
    response = ""
    while row.next():
        response += str(row.value(0))
    return response

if __name__ == "__main__":
    dataB = db.db.DBManager(DATABASE)

    app = QApplication([])
    mainWindow = gui.mainWindow.MainWindow(dataB)
    mainWindow.show()
    app.exec()
