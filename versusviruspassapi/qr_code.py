from base64 import b64encode, b64decode
from datetime import datetime, timedelta
from typing import List

from Crypto import Random
from Crypto.PublicKey.RSA import generate
from Crypto.Signature.

test_id_counter: int = 1
pub_keys: List[bytes] = []


class QRCode:
    __delimiter = '|'
    __date_format = '%d.%m.%Y'
    test_id: int = 0
    test_date: datetime = datetime(1, 1, 1)
    immunity_duration: timedelta = timedelta(0)
    antibody_id: int = 0
    salt: str = ''
    signature: str = ''

    def verify_signature(self) -> bool:
        data = b64encode(self.__delimiter.join([
            str(self.test_id),
            self.test_date.strftime(self.__date_format),
            self.immunity_duration.days,
            self.antibody_id,
            self.salt,
        ]))
        #TODO: Verify signature

    @classmethod
    def create_qr_code(cls, test_date: datetime, immunity_duration: timedelta, antibody_id: int, privk: bytes)\
            -> 'QRCode':
        global test_id_counter
        test_id_counter += 1
        qr_code = QRCode()
        qr_code.test_id = test_id_counter
        qr_code.test_date = test_date
        qr_code.immunity_duration = immunity_duration
        qr_code.antibody_id = antibody_id
        qr_code.salt = Random.new().read(32).decode('utf-8')
        return qr_code

    def to_b64(self) -> str:
        return b64encode(self.__delimiter.join([
            str(self.test_id),
            self.test_date.strftime(self.__date_format),
            self.immunity_duration.strftime(self.__date_format),
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
        qr_code.immunity_duration = datetime.strptime(expiration_date_str, cls.__date_format)
        qr_code.antibody_id = int(antibody_id_str)
        qr_code.salt = salt
        qr_code.signature = signature
        return qr_code