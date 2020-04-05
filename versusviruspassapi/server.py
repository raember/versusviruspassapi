from flask_restful import Api as FlaskApi, Resource
from flask_restful.reqparse import RequestParser
from .blockchain import Block
from .qr_code import QRCode


class ImmunityCertificate(Resource):
    def post(self, qr_code_b64: str, subject_id: str):
        """
        Validates immunity certificate and makes a block
        """
        qr_code = QRCode.from_b64(qr_code_b64)
        if not qr_code.verify_signature():
            return "Signature could not be verified", 406
        block = Block.from_qr_code_and_subject_id(qr_code, subject_id)
        parser = RequestParser()
        parser.add_argument('testID')
        parser.add_argument('testIDsig')
        parser.add_argument('testpubkey')
        parser.add_argument('antibodyID')
        parser.add_argument('testResult')
        parser.add_argument('subjectID')
        args = parser.parse_args()
        #TODO: Verify test ID authenticity and make a block

    def get(self, qr_code_b64: str, subject_id: str):
        pass
        #TODO: Get block from blockchain matching the test ID or return an error if no match


class Api(FlaskApi):
    def __init__(self, **kwargs):
        super(Api, self).__init__(**kwargs)
        self.add_resource(ImmunityCertificate, '/cert/<string:qr_code_b64>/<string:subject_id>')
