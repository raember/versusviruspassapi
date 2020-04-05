import json
import logging
from _sha256 import sha256
from datetime import datetime, timedelta
from typing import List

from Crypto.Hash.SHA256 import SHA256Hash

from versusviruspassapi.qr_code import QRCode


class Block:
    last_block: bytes = b''
    test_id: int = 0
    test_level: int = 1
    test_date: datetime = datetime(1, 1, 1)
    immunity_duration: int = 0
    antibody: str = ''
    test_result: bool = False
    signature: bytes = b''
    proof: bytes = b''
    nonce: int = 0

    @property
    def hashable_fields(self) -> str:
        return "|".join([
            self.last_block.decode('latin1'),
            str(self.test_id),
            str(self.test_level),
            self.test_date.strftime('%d.%m.%Y'),
            str(self.immunity_duration),
            self.antibody,
            str(self.test_result),
            self.signature.decode('latin1'),
            self.proof.decode('latin1'),
            str(self.nonce),
        ])

    def calculate_hash(self) -> bytes:
        return SHA256Hash(self.hashable_fields.encode('latin1')).digest()

    def mine_block(self, difficulty: int):
        """
        Performs the proof of work by finding a hash that has a set number of leading zeros by adjusting the nonce

        :param difficulty: The amount of leading zeros the hash needs to have until the block is considered mined.
        """
        self.nonce = 0
        while not self.calculate_hash().startswith(b'0' * difficulty):
            self.nonce += 1

    @classmethod
    def create(cls, qr_code: QRCode, subject_id: str) -> 'Block':
        block = Block()
        block.test_id = qr_code.test_id
        block.test_level = qr_code.test_level
        block.test_date = qr_code.test_date
        block.immunity_duration = qr_code.immunity_duration.days
        block.antibody = qr_code.antibody
        block.test_result = qr_code.test_result
        block.signature = qr_code.signature
        block.proof = SHA256Hash((subject_id + qr_code.salt).encode()).digest()
        return block

    def __str__(self):
        return f"Immunity Test #{self.test_id}. " \
               f"{self.antibody}: {self.test_result} " \
               f"from {self.test_date} until {self.test_date + timedelta(days=self.immunity_duration)}"


class BlockChain:
    log: logging.Logger
    chain: List[Block]
    difficulty: int

    def __init__(self, difficulty: int):
        self.log = logging.getLogger(self.__class__.__name__)
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty

    # noinspection PyMethodMayBeStatic
    def create_genesis_block(self) -> Block:
        genesis_block = Block()
        return genesis_block

    def append_block(self, block: Block) -> bool:
        block.last_block = self.chain[-1].calculate_hash()
        block.mine_block(self.difficulty)
        self.chain.append(block)
        return True
