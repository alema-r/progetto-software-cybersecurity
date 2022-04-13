'''
Modules that ask user's role and initialize connection to the node corresponding to user role inserted. Here it is
also injected proof of authority middleware in order to accomplish transaction on the blockcchain.

You can access the web3 instance of the connection established with the blockchain by importing this module and
accessing it doing connection.web3

Since every subsequent `import` after the first uses the cached module
instead of re-evaluating it, it is guaranteed that every module that import
connection, refer to the same instance.
'''

import inquirer
from inquirer.themes import load_theme_from_dict
from web3 import Web3
from web3.middleware import geth_poa_middleware

from .theme_dict import theme

BASE_URL = "http://127.0.0.1:2200"
print("Welcome!")
questions = [
    inquirer.List('role',
                  message="Specify your role",
                  choices=[("Client", 0), ("Supplier", 1), ("Transformer", 2), ("Exit", -1)],
                  )
]

answers = inquirer.prompt(questions, theme=load_theme_from_dict(theme))
if answers is not None and answers['role'] != -1:
    # getting user role to instantiate connection to the correct node
    role = answers['role']
    # creating the node address url with the given role
    url = BASE_URL + str(role)
    # creates web3 connection to the selected node
    web3 = Web3(Web3.HTTPProvider(url))
    # injects proof of authority middleware to complete transactions
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
else:
    print("Goodbye have a nice day")
    exit(0)