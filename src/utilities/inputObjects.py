from datetime import date
import re

class DocumentStruct:
    """DocumentList is struct what holds id and name of document"""
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class DocumentList:
    """Wrapper around list of DocumentStruct"""
    _docs = []
    
    def append(self, doc: DocumentStruct) -> None:
        self._docs.append(doc)

    def search(self, name: str) -> list:
        return [ d for d in self._docs if d.name == name ]

    def searchById(self, id: int) -> list:
        return [ d for d in self._docs if d.id == id ]

    def get(self) -> list:
        return self._docs


class AccountStruct:
    """AccountStruct is struct of account (id, name, no)"""
    id: int
    name: str
    no: int

    def __init__(self, id: int, name: str, no: str):
        self.id = id
        self.name = name
        self.no = no

    def present(self) -> str:
        return f'{self.name} ({self.no})'

    @staticmethod
    def parsePresent(s: str) -> (str, int):
        m = re.search("(.+) \((\d+)\)", s)
        if m != None:
            return (m.groups()[0], m.groups()[1])

        return ("",-1)


class AccountList:
    """Wrapper around list of AccountStruct"""
    _accounts = []

    def append(self, acc: AccountStruct) -> None:
        self._accounts.append(acc)

    def search(self, name: str) -> list:
        return [ a for a in self._accounts if a.present() == name or a.no == name ]

    def searchById(self, id: int) -> list:
        return [ a for a in self._accounts if a.id == id ]

    def get(self) -> list:
        return self._accounts

class AccountRecord:
    id: int
    documenttype: int
    debit: float
    kredit: float
    price: float

    def __init__(self, id: int, documenttype: int, debit: float, kredit: float, price: float):
        self.id = id
        self.documenttype = documenttype
        self.debit = debit
        self.kredit = kredit
        self.price = price
    def __str__(self):
        return f"AccountRecord id: {self.id}, documenttype: {self.documenttype}, debit: {self.debit}, kredit: {self.kredit}, price: {self.price}"

class InputDocumentStruct:
    id: str
    _id: int = 0
    document: str
    _documentId: int = 0
    debit: str
    _debitId: int = 0
    kredit: str
    _kreditId: int = 0
    price: str
    _price: float = 0
    notice: str
    date: str
    _date: int = 0

    def __init__(self, id: str, document: str, debit: str, kredit: str, price: str, notice: str, date: str):
        self.id = id
        self.document = document
        self.debit = debit
        self.kredit = kredit
        self.price = price
        self.notice = notice
        self.date = date

    def get(self) -> tuple:
        """Get returns all validated and formated input values"""
        return self._id, self._documentId, self._debitId, self._kreditId, self._price, self.notice, self._date

    def validate(self, documents: DocumentList, accounts: AccountList) -> list:
        """ Validate checks all input values and convert them into proper types
            what can be inserted into DB
        """
        errors = []
        id, error = self._validateDocId(self.id)
        if error:
            errors.append(error)
        else:
            self._id = id

        doc, error = self._validateDoc(documents)
        if error:
            errors.append(error)
        else:
            self._documentId = doc.id
        
        acc, error = self._validateAccount(self.debit, accounts)
        if error:
            errors.append(error)
        else:
            self._debitId = acc.id

        acc, error = self._validateAccount(self.kredit, accounts)
        if error:
            errors.append(error)
        else:
            self._kreditId = acc.id

        price, error = self._validatePrice(self.price)
        if error:
            errors.append(error)
        else:
            self._price = price

        date, error = self._validateDate(self.date)
        if error:
            errors.append(error)
        else:
            self._date = date
        return errors

    def _validateDocId(self, id: int) -> tuple:
        if not id:
            return None, "- chyba v čísle dokladu"
        conv = int(id)
        return conv, ""

    def _validateDoc(self, documents: DocumentList) -> tuple:
        if not self.document:
            return None, "- typ dokumentu nesmí být prázdný"

        foundDocument = documents.search( self.document )
        if len(foundDocument) == 0:
            return None, "- nebyl nalezen typ dokumentu, zadejte předdefinovaný"

        if len(foundDocument) > 1:
            return None, "- bylo nalezeno více typů dokumentu, je třeba upravit databázi preddefinovaných typů dokumentů"

        return foundDocument[0], ""
        
    def _validateAccount(self, accountName, accounts: AccountList) -> tuple:
        if not accountName:
            return None, f"- účet MD/D musí být zadán"
        
        foundAccount = accounts.search( accountName )
        if len(foundAccount) == 0:
            return None, f'- nebly nalezen účet "{accountName}", zadejte předdefinovaný'

        if len(foundAccount) > 1:
            return None, "- bylo nalezeno více účtů, je třeba upravit databázi předdefinovaných typů účtů"

        return foundAccount[0], ""
    
    def _validatePrice(self, price) -> tuple:
        if not price:
            return 0, "- cena nesmí být prázdná"
        
        try:
            priceN = float(price)
            return priceN, None
        except Exception as e:
            print(f"Error during validating price {price}: {e}")
            return 0, f'- cena musí být desetinné číslo'

    def _validateDate(self, date) -> tuple:
        if not date:
            return 0, "- datum musí být číslo"
        try:
            dateN = int(float(date))
            print(f"Date validate {date}-{dateN}")
            return dateN, None
        except Exception as e:
            print(f"Error during validating date {date}: {e}")
            return 0, "- datum musí být číslo"
