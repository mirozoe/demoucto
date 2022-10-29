from PyQt5.QtWidgets import QMessageBox


class MessageBox(QMessageBox):

    def __init__(self, type, text: str):
        super(MessageBox, self).__init__()

        self.setIcon(type)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Ok)
        self.buttonClicked.connect(self.cancel)
        self.exec()

    def cancel(self):
        self.close()