from flask import Flask
from versusviruspassapi import Api
from versusviruspassapi.blockchain import BlockChain

if __name__ == '__main__':
    app = Flask('server')
    block_chain = BlockChain(4)
    #TODO: Populate blockchain with example data

    api = Api(app=app, block_chain=block_chain)
    app.run(debug=True)
