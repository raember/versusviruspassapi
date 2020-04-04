from flask import Flask
from versusviruspassapi import Api

if __name__ == '__main__':
    app = Flask('server')
    api = Api(app=app)
    app.run(debug=True)
