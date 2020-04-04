from flask_restful import Api as FlaskApi, Resource
from flask_restful.reqparse import RequestParser


class ImmunityCertificate(Resource):
    def post(self, test_id):
        """
        Validates immunity certificate and makes a block
        """
        parser = RequestParser()
        parser.add_argument('testID')
        parser.add_argument('testIDsig')
        parser.add_argument('testpubkey')
        parser.add_argument('antibodyID')
        parser.add_argument('testResult')
        parser.add_argument('subjectID')
        args = parser.parse_args()
        #TODO: Verify test ID authenticity and make a block

    def get(self, test_id: str):
        pass
        #TODO: Get block from blockchain matching the test ID or return an error if no match


class Api(FlaskApi):
    def __init__(self, **kwargs):
        super(Api, self).__init__(**kwargs)
        self.add_resource(ImmunityCertificate, '/cert/<string:test_id>')
