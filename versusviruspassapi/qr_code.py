from base64 import b64encode, b64decode
from datetime import datetime


class QRCode:
    __delimiter = '|'
    __date_format = '%d.%m.%Y'
    test_id: int = 0
    test_date: datetime = datetime(1, 1, 1)
    expiration_date: datetime = datetime(1, 1, 1)
    antibody_id: int = 0
    signature: str = ''
    salt: bytes = b''

    def verify_signature(self) -> bool:
        data = b64encode(self.__delimiter.join([
            str(self.test_id),
            self.test_date.strftime(self.__date_format),
            self.expiration_date.strftime(self.__date_format),
            self.antibody_id,
            self.salt,
        ]))
        #TODO: Verify signature


    def to_b64(self) -> str:
        return b64encode(self.__delimiter.join([
            str(self.test_id),
            self.test_date.strftime(self.__date_format),
            self.expiration_date.strftime(self.__date_format),
            self.antibody_id,
            self.salt,
            self.signature,
        ]))

    @classmethod
    def from_b64(cls, b64: str) -> 'QRCode':
        test_id_str, test_date_str, expiration_date_str, antibody_id_str, signature, salt = \
            tuple(str(b64decode(b64)).split(cls.__delimiter, maxsplit=5))
        qr_code = QRCode()
        qr_code.test_id = int(test_id_str)
        qr_code.test_date = datetime.strptime(test_date_str, cls.__date_format)
        qr_code.expiration_date = datetime.strptime(expiration_date_str, cls.__date_format)
        qr_code.antibody_id = int(antibody_id_str)
        qr_code.salt = salt
        qr_code.signature = signature
        return qr_code