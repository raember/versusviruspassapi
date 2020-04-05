from datetime import datetime, timedelta
from typing import Tuple, List
from urllib.parse import unquote_plus

from Crypto.PublicKey.RSA import RsaKey
from flask_restful import Api as FlaskApi, Resource
from flask_restful.reqparse import RequestParser
from .blockchain import Block, BlockChain
from .qr_code import QRCode


block_chain: BlockChain
pub_keys: List[RsaKey] = []


class ImmunityCertificate(Resource):
    def post(self) -> Tuple[dict, int]:
        """
        Validates the immunity certificate and makes a block.

        Verifies the signature of the QR code and makes sure the test has not been submitted before.
        Then, the immunity certificate will be submitted to the blockchain.
        :param qr_code_b64: The data encoded in the qr code, all base64 encoded.
        :param subject_id: The identifying number of the challengee.
        :return: A json dict with a `success` boolean and a `msg`, plus the HTTP status code.
        """
        parser = RequestParser()
        parser.add_argument('qr_code_b64')
        parser.add_argument('subject_id')
        args = parser.parse_args()
        qr_code = QRCode.from_b64(unquote_plus(args['qr_code_b64']))
        print(f"Submit: Test #{qr_code.test_id} for {args['subject_id']}")
        # Please look away for a few lines. May the gods avert their eyes and spare this sinful soul of mine.
        global pub_keys
        verified = False
        for pub_key in pub_keys:
            if qr_code.verify_signature(pub_key):
                verified = True
                break
        if not verified:
            return {
                       'success': False,
                       'msg': "Signature could not be verified"
                   }, 406
        block = Block.create(qr_code, args['subject_id'])
        global block_chain
        for block in block_chain.chain:
            if block.test_id == qr_code.test_id:
                return {
                    'success': False,
                    'msg': "Test has already been submitted before"
                }, 406
        if block_chain.append_block(block):
            return {
                'success': True,
                'msg': "Block appended to the blockchain"
            }, 201
        return {
            'success': False,
            'msg': "Block was faulty and could not be appended to the blockchain"
        }, 500

    def get(self) -> Tuple[dict, int]:
        """
        Verifies the authenticity of the test result and it's credibility.

        Searches for the block in the blockchain that matches the given test ID and verifies that it belongs to the
        given subject.
        :param qr_code_b64: The data encoded in the qr code, all base64 encoded.
        :param subject_id: The identifying number of the challengee.
        :return: A json dict with a `success` boolean and a `msg`, plus the HTTP status code.
        """
        parser = RequestParser()
        parser.add_argument('qr_code_b64')
        parser.add_argument('subject_id')
        args = parser.parse_args()
        qr_code = QRCode.from_b64(unquote_plus(args['qr_code_b64']))
        print(f"Challenge: Test #{qr_code.test_id} for {args['subject_id']}")
        # Please look away for a few lines. May the gods avert their eyes and spare this sinful soul of mine.
        global pub_keys
        verified = False
        for pub_key in pub_keys:
            if qr_code.verify_signature(pub_key):
                verified = True
                break
        if not verified:
            return {
                       'success': False,
                       'msg': "Signature could not be verified"
                   }, 406
        global block_chain
        # noinspection PyTypeChecker
        block: Block = None
        for block in block_chain.chain:
            if block.test_id == qr_code.test_id:
                break
        if block is None:
            return {
                'success': False,
                'msg': "No matching block found"
            }, 404
        challengee_block = Block.create(qr_code, args['subject_id'])
        if challengee_block.proof == block.proof:
            if block.test_date + timedelta(days=block.immunity_duration) > datetime.now():
                return {
                    'success': True,
                    'msg': "Challengee data verified"
                }, 200
            return {
                'success': False,
                'msg': "Challengee data could be verified but is expired"
            }, 406
        return {
            'success': False,
            'msg': "Challengee data could not be verified or it has expired"
        }, 406


class Api(FlaskApi):
    def __init__(self, **kwargs):
        global block_chain, pub_keys
        block_chain = kwargs.get('block_chain', BlockChain(4))
        pub_keys = kwargs.get('pub_keys', [])
        if 'block_chain' in kwargs:
            del(kwargs['block_chain'])
        if 'pub_keys' in kwargs:
            del(kwargs['pub_keys'])
        super(Api, self).__init__(**kwargs)
        self.add_resource(ImmunityCertificate, '/cert')
