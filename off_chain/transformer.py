import inquirer
from inquirer.themes import load_theme_from_dict
from web3 import Web3, exceptions

from . import blockchain
from .theme_dict import theme
from . import validation


def get_updatable_user_products(user_address):
    '''This function filters the products stored in the blockhain. It returns a list of the products that are owned by the 
    current user.

    Args:
        products (`List[Product]`): the list of the products stored in the blockhain
        user_address (`ChecksumAddress`): the adress of the current user

    Returns:
        `list[Product]`: the list of the products owned by the current user
    '''
    all_products = blockchain.get_all_products()
    return list(filter(lambda p: (p.address == user_address and not p.is_ended), all_products))


def add_transformation(user_address):
    """This function lets the transformer user add a new trasformation to the production chain of a product that they own.

    Args:
        user_address(`ChecksumAddress`): the address of the current user
    """
    print("Follow the instructions to add a transformation to a product. You can cancel operation in any moment "
          "by pressing Ctrl+C")
    # gets the products associated with the current user
    user_products = get_updatable_user_products(user_address)
    questions = [
        inquirer.List(
            "product_id",
            message="What product do you want to update?",
            choices=[(product.name, product.product_id)
                     for product in user_products],
            carousel=True
        ),
        inquirer.Text(
            "CF",
            message="Insert the carbon footprint value of this transformation",
            validate=validation.carbon_fp_input_validation,
        ),
        inquirer.Confirm(
            'final',
            message="Is this the final transformation?",
        )
    ]
    answers = inquirer.prompt(questions, theme=load_theme_from_dict(theme))
    if answers is not None:
        # asks the user for confirmation
        if answers['final']:
            print(
                "BE CAREFUL, after this operation the product will be no longer modifiable")
        confirm_question = [inquirer.Confirm(
            "confirm",
            message=f"Do you want to add this transformation, with a carbon footprint of {answers['CF']}, to the selected product?"
        )]
        confirm = inquirer.prompt(
            confirm_question, theme=load_theme_from_dict(theme))
        # if the user confirms the transaction is started.
        if confirm['confirm'] and confirm is not None:
            success = blockchain.add_transformation_on_blockchain(
                int(answers['CF']), answers['product_id'], answers['final'])
            if success:
                print("Operation completed successfully")


def transfer_product(user_address):
    '''This function lets the transformer user transfer the property of a product to another transformer

    Args:
        user_address (`ChecksumAddress`): the list of the products that the user currently owns
    '''
    # get products associated with user address
    user_products = get_updatable_user_products(user_address)
    print("Follow the instructions to complete transfer process. You can cancel operation in any moment "
          "by pressing Ctrl+C")
    questions = [
        inquirer.List(
            "product_id",
            message="What product do you want to transfer?",
            choices=[(product.name[:22]+"..." if len(product.name > 25)
                      else product.name, product.product_id) for product in user_products],
            carousel=True
        ),
        inquirer.Text(
            "transformer",
            message="Insert the address of the transformer to who you want to transfer the product",
            validate=validation.transformer_address_validation,
        )
    ]
    answers = inquirer.prompt(questions, theme=load_theme_from_dict(theme))
    # asks the user for confirmation
    if answers is not None:
        confirm_question = [inquirer.Confirm(
            "confirm",
            message=f"Do you want to transfer the selected product to the address {answers['transformer']}?"
        )]
        confirm_answer = inquirer.prompt(
            confirm_question, theme=load_theme_from_dict(theme))

        # if the user confirms the transaction is started.
        if confirm_answer["confirm"]:
            success = blockchain.transfer_product_on_blockchain(
                Web3.toChecksumAddress(answers['transformer']), answers["product_id"])
            if success:
                print("Operation completed succesfully")


def create_new_product():
    """This function lets the transformer create a new product, by selecting the necessary raw materials
    """
    print("Follow the instructions to create new product. You can cancel operation in any moment "
          "by pressing Ctrl+C")
    questions = [
        inquirer.Text(
            "name",  # asks the name of the product
            message="Type the name of the product you want to create",
            validate=validation.name_input_validation
        ),
        inquirer.Checkbox(
            "raw_materials",  # The user selects the raw materials to use.
            message="Select a raw material to use",
            choices=[(material.__str__(), material.material_id)
                     for material in blockchain.get_raw_material_not_used()],
        )
    ]
    answers = inquirer.prompt(questions, theme=load_theme_from_dict(theme))
    if answers is not None:
        # asks the user for confirmation
        confirm_question = [inquirer.Confirm(
            "confirm",
            message=f"Do you want to create the product \"{answers['name']}\" with the selected materials?"
        )]
        confirm_answer = inquirer.prompt(
            confirm_question, theme=load_theme_from_dict(theme))
        # if the user confirms the transaction is started.
        if confirm_answer['confirm'] and confirm_answer is not None:
            success = blockchain.create_new_product_on_blockchain(
                answers['name'], answers['raw_materials'])
            if success:
                print("Operation completed successfully")