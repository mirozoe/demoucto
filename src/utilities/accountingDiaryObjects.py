
from utilities.inputObjects import InputDocumentStruct


class AccountingDiaryObject:
    id: int
    docTypeId: int
    docTypeName: str
    debitId: int
    debit: str
    kreditId: int
    kredit: str
    price: float
    notice: str
    date: str
    columns: int = 7

    def __init__(self, id, docTypeId, docTypeName, debitId, debit, kreditId, kredit, price, notice, date):
        self.id = id
        self.docTypeId = docTypeId
        self.docTypeName = docTypeName
        self.debitId = debitId
        self.debit = debit
        self.kreditId = kreditId
        self.kredit = kredit
        self.price = price
        self.notice = notice
        self.date = date

    def toInputDocumentStruct(self) -> InputDocumentStruct:
        return InputDocumentStruct(str(self.id), str(self.docTypeId), str(self.debitId), str(self.kreditId), str(self.price), self.notice, self.date)