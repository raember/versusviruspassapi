from datetime import datetime
from typing import Tuple

from flask_restful import Api as FlaskApi, Resource
from flask_restful.reqparse import RequestParser
from .blockchain import Block, BlockChain
from .qr_code import QRCode


block_chain: BlockChain


class ImmunityCertificate(Resource):
    def post(self, qr_code_b64: str, subject_id: str) -> Tuple[dict, int]:
        """
        Validates the immunity certificate and makes a block.

        Verifies the signature of the QR code and makes sure the test has not been submitted before.
        Then, the immunity certificate will be submitted to the blockchain.
        :param qr_code_b64: The data encoded in the qr code, all base64 encoded.
        :param subject_id: The identifying number of the challengee.
        :return: A json dict with a `success` boolean and a `msg`, plus the HTTP status code.
        """
        qr_code = QRCode.from_b64(qr_code_b64)
        if not qr_code.verify_signature():
            return {
                       'success': False,
                       'msg': "Signature could not be verified"
                   }, 406
        block = Block.from_qr_code_and_subject_id(qr_code, subject_id)
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

    def get(self, qr_code_b64: str, subject_id: str) -> Tuple[dict, int]:
        """
        Verifies the authenticity of the test result and it's credibility.

        Searches for the block in the blockchain that matches the given test ID and verifies that it belongs to the
        given subject.
        :param qr_code_b64: The data encoded in the qr code, all base64 encoded.
        :param subject_id: The identifying number of the challengee.
        :return: A json dict with a `success` boolean and a `msg`, plus the HTTP status code.
        """
        qr_code = QRCode.from_b64(qr_code_b64)
        if not qr_code.verify_signature():
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
        challengee_block = Block.from_qr_code_and_subject_id(qr_code, subject_id)
        if challengee_block.proof == block.proof and block.expiration_date < datetime.now():
            return {
                'success': True,
                'msg': "Challengee data verified"
            }, 200
        return {
            'success': False,
            'msg': "Challengee data could not be verified or expired"
        }, 406


class Api(FlaskApi):
    def __init__(self, **kwargs):
        super(Api, self).__init__(**kwargs)
        global block_chain
        block_chain = kwargs.get('block_chain', BlockChain(4))
        self.add_resource(ImmunityCertificate, '/cert/<string:qr_code_b64>/<string:subject_id>')
