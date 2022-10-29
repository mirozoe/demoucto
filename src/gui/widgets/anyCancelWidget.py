from PyQt5.QtWidgets import QAction, QDialog, QHBoxLayout, QMainWindow, QMenuBar, QLabel, QPushButton, QVBoxLayout, QWidget

class AnyCancel(QWidget):
    """This is basic widget what is used in modal windows where needs to be two possibilities (OK, Cancel)"""
    
    def __init__(self, saveTitle, cancelTitle, savecallback, cancelcallback):
        super(AnyCancel, self).__init__()
        hLayout = QHBoxLayout()

        save = QPushButton(saveTitle)
        save.clicked.connect(savecallback)

        cancel = QPushButton(cancelTitle)
        cancel.clicked.connect(cancelcallback)

        hLayout.addWidget(save)
        hLayout.addSpacing(2)
        hLayout.addWidget(cancel)
        self.setLayout(hLayout)