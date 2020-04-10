from datetime import datetime, timedelta
from itertools import repeat
from urllib.parse import quote_plus
from flask import Flask
from versusviruspassapi import Api
from versusviruspassapi.blockchain import BlockChain, Block
from versusviruspassapi.qr_code import QRCode
from versusviruspassapi.util import create_pub_priv_key_key_pair


def register_block(method: str, qr_code: QRCode, subject: str) -> Block:
    qrb64 = quote_plus(qr_code.to_b64())
    print(f"{method} http://127.0.0.1:5000/cert?qr_code_b64={qrb64}&subject_id={subject}")
    print(f" QR code: {qrb64}")
    print(f" Subject: {subject}")
    return Block.create(qr_code=qr_code, subject_id=subject)


if __name__ == '__main__':
    app = Flask('server')
    block_chain_mock = BlockChain(1)
    issuer1 = create_pub_priv_key_key_pair()
    issuer2 = create_pub_priv_key_key_pair()
    pub_keys_mock = [issuer1.publickey(), issuer2.publickey()]
    block_chain_mock.append_block(register_block('GET', QRCode.create_qr_code(
        test_level=3,
        test_date=datetime.now(),
        immunity_duration=timedelta(days=356),
        antibody='Sars-COVID-19',
        test_result=True,
        priv_key=issuer1,
    ), 'X001'))
    register_block('POST/GET', QRCode.create_qr_code(
        test_level=2,
        test_date=datetime.now(),
        immunity_duration=timedelta(days=128),
        antibody='Sars-COVID-19',
        test_result=True,
        priv_key=issuer2,
    ), 'X002')
    api = Api(app=app, block_chain=block_chain_mock, pub_keys=pub_keys_mock)
    app.run(debug=True)
