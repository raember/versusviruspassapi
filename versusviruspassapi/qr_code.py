from base64 import b64encode, b64decode
from datetime import datetime, timedelta
from logging import Logger, getLogger
from typing import List

from Crypto import Random
from Crypto.Hash.SHA256 import SHA256Hash
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import PKCS1_v1_5

test_id_counter: int = 1


class QRCode:
    __delimiter = '|'
    __date_format = '%d.%m.%Y'
    log: Logger = None

    test_id: int = 0
    test_level: int = 1
    test_date: datetime = datetime(1, 1, 1)
    immunity_duration: timedelta = timedelta(0)
    antibody: int = 0
    test_result: bool = False
    salt: str = ''
    signature: bytes = b''

    def __init__(self):
        self.log = getLogger(self.__class__.__name__)

    @property
    def signable_data(self) -> List[str]:
        return [
            str(self.test_id),
            str(self.test_level),
            self.test_date.strftime(self.__date_format),
            str(self.immunity_duration.days),
            self.antibody,
            str(self.test_result),
            b64encode(self.salt.encode('latin1')).decode('latin1'),
        ]

    @property
    def signable_hash(self) -> SHA256Hash:
        return SHA256Hash.new(b64encode(self.__delimiter.join(self.signable_data).encode('latin1')))

    def verify_signature(self, pub_key: RsaKey) -> bool:
        signable_hash = self.signable_hash
        signature = b64encode(self.signature).decode('latin1')
        try:
            # noinspection PyTypeChecker
            PKCS1_v1_5.new(pub_key).verify(signable_hash, signature)
            return True
        except Exception as e:
            self.log.error(f"Failed to verify signature: {e}")
            return False

    @classmethod
    def create_qr_code(
            cls,
            test_level: int,
            test_date: datetime,
            immunity_duration: timedelta,
            antibody: str,
            test_result: bool,
            priv_key: RsaKey) -> 'QRCode':
        global test_id_counter
        qr_code = QRCode()
        qr_code.test_id = test_id_counter
        test_id_counter += 1
        qr_code.test_level = test_level
        qr_code.test_date = test_date
        qr_code.immunity_duration = immunity_duration
        qr_code.antibody = antibody
        qr_code.test_result = test_result
        qr_code.salt = Random.new().read(32).decode('latin1')
        # noinspection PyTypeChecker
        qr_code.signature = PKCS1_v1_5.new(priv_key).sign(qr_code.signable_hash)
        return qr_code

    def to_b64(self) -> str:
        return b64encode(
            self.__delimiter.join([
                *self.signable_data,
                b64encode(self.signature).decode('latin1')
            ]).encode('latin1')
        ).decode('latin1')

    @classmethod
    def from_b64(cls, b64: str) -> 'QRCode':
        test_id_str, test_level_str, test_date_str, immunity_duration_str, antibody, test_result_str, salt, signature = \
            tuple(b64decode(b64).decode('latin1').split(cls.__delimiter, maxsplit=7))
        qr_code = QRCode()
        qr_code.test_id = int(test_id_str)
        qr_code.test_level = int(test_level_str)
        qr_code.test_date = datetime.strptime(test_date_str, cls.__date_format)
        qr_code.immunity_duration = timedelta(days=int(immunity_duration_str))
        qr_code.antibody = antibody
        qr_code.test_result = True if test_result_str == 'True' else False
        qr_code.salt = b64decode(salt.encode('latin1')).decode('latin1')
        qr_code.signature = b64decode(signature.encode('latin1'))
        return qr_code