import json
import logging
from _sha256 import sha256
from datetime import datetime
from typing import List

from versusviruspassapi.qr_code import QRCode


class Block:
    last_block: bytes
    test_id: int = 0
    test_date: datetime = datetime(1, 1, 1)
    expiration_date: datetime = datetime(1, 1, 1)
    antibody_id: int = 0
    signature: str = ''
    proof: bytes
    nonce: int = 0

    def __hash__(self) -> bytes:
        # stomach = sha256()
        # stomach.update(bytes(self.test_id))
        # stomach.update(self.test_date.strftime('%d.%m.%Y').encode('utf8'))
        # stomach.update(self.expiration_date.strftime('%d.%m.%Y').encode('utf8'))
        # stomach.update(bytes(self.antibody_id))
        # stomach.update(bytes(self.nonce))
        return sha256(json.dumps(self.__dict__, sort_keys=True).encode()).hexdigest()

    def mine_block(self, difficulty: int):
        """
        Performs the proof of work by finding a hash that has a set number of leading zeros by adjusting the nonce

        :param difficulty: The amount of leading 0 bytes the hash needs to have until the block is considered mined.
        """
        while not self.__hash__().startswith(b'0' * difficulty):
            self.nonce += 1

    @classmethod
    def from_qr_code_and_subject_id(cls, qr_code: QRCode, subject_id: str) -> 'Block':
        block = Block()
        block.test_id = qr_code.test_id
        block.test_date = qr_code.test_date
        block.expiration_date = qr_code.expiration_date
        block.antibody_id = qr_code.antibody_id
        block.signature = qr_code.signature
        block.proof = subject_id
        return block


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
        if len(block.__dict__) != 6:
            self.log.error(f"Block fields count mismatch! Block not added to chain.")
            return False
        block.last_block = hash(self.chain[-1])
        block.mine_block(self.difficulty)
        self.chain.append(block)
        return True