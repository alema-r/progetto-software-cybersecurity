"""Module that implements a base controller class
"""
from functools import singledispatch
from typing import List
from requests import exceptions as requests_exceptions

from eth_typing import ChecksumAddress
from web3 import Web3
from web3 import exceptions as solidity_exceptions

from off_chain import contracts
from off_chain import event_logs
from off_chain.models import Product, RawMaterial, Transformation


class BlockChain:
    """Base controller class"""

    def __init__(self, web3: Web3):
        self.web3 = web3
        self.user_contract = contracts.build_user_contract(web3)
        self.event_logs = event_logs.EventLogs(
            contracts.build_cf_contract(self.user_contract, web3)
        )

    def set_account_as_default(self, user_role: int, address: str) -> None:
        """
        Function used to check if user address corresponds to the given role and set current
        user address as default web3 account in order to accomplish transactions
        Args:
            user_role: (int): the integer identifier of the role chose by the current user
            address: (Address): address of current logged user

        Raises:
            Exception: Custom general error raised if a non planned error occurs

        """
        try:
            # Checking for correct account format
            account = self.web3.toChecksumAddress(address)
            # If the account is inside the list of known accounts of the block
            if account in self.web3.eth.accounts:
                self.web3.geth.personal.unlock_account(account, "")
                # Calling the method to check current account role inside user contract
                real_role = self.get_user_role(account)
                # If the account isn't registered inside the contract
                if real_role == 0 and user_role != 0:
                    # The user is created with the given role inside the
                    self.web3.eth.default_account = account
                    tx_hash = self.user_contract.functions.createUser(
                        user_role
                    ).transact()
                    self.web3.eth.wait_for_transaction_receipt(tx_hash)
                else:
                    # The account is set as the default account
                    self.web3.eth.default_account = account
            # If the account isn't inside the current block's list of accounts
            else:
                # An error is raised
                raise Exception
        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
        except solidity_exceptions.ContractLogicError as error:
            print(error)
        except Exception:
            raise Exception(
                "Error: it's impossible to verify your role and address, please try again"
            )

    def get_user_role(self, address: ChecksumAddress = None) -> int:
        """Retrieves the user role of the address (if specified) otherwise it returns
        the role of the caller.

        Args:
            address (ChecksumAddress, optional): address of a user. Defaults to None.

        Returns:
            int: the role of the user (0 = not registered, 1 = supplier, 2 = transformer)
        """
        try:
            if address is None:
                role = self.user_contract.functions.getRole().call()
            else:
                role = self.user_contract.functions.getRole(address).call()
        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
            return None
        except solidity_exceptions.ContractLogicError as error:
            print(error)
            return None
        else:
            return role

    def get_product(self, product_id: int) -> Product:
        """Gets the product from the blockchain with no information on raw materials
        and transformations.

        Args:
            product_id (`int`): the id of the product to get

        Returns:
            `Product`: a product from the blockchain
        """
        try:
            prod = self.user_contract.functions.getProductById(product_id).call()
        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
            return None
        except solidity_exceptions.ContractLogicError as error:
            print(error)
            return None
        else:
            return Product.from_blockchain(prod)

    # @singledispatch decorator allows function overloading depending on argument type
    # (in this case argument is a Product Object)
    # doc: https://docs.python.org/3/library/functools.html#functools.singledispatch
    @singledispatch
    def get_product_details(self, product: int) -> Product:
        """Gets information about raw material used and transformations
        performed on the specified product

        Args_
            product (`int`): the product id

        Returns
            `Product`: a product from the blockchain, with all the info
        """
        # The information regarding the raw materials used and the transformations implemented
        # are taken from the events emitted on the blockchain
        try:
            rm_events = self.event_logs.get_raw_materials_used_events(product)
            transformation_events = self.event_logs.get_transformations_events(product)
        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
            return None
        else:
            product = self.get_product(product)
            product.rawMaterials = [
                RawMaterial.from_event(event=ev) for ev in rm_events
            ]
            product.transformations = [
                Transformation.from_event(event=ev) for ev in transformation_events
            ]
            return product

    @get_product_details.register
    def _(self, product: Product) -> Product:
        """Overload of the `get_product_details` function. Gets information about
        raw material used and transformations performed on the specified product.

        Args:
            product (`Product`): the product object with the requested info

        Returns:
            `Product`: a product from the blockchain, with all the info
        """
        # The info regarding the raw materials used and the transformations implemented
        # are taken from the events emitted on the blockchain
        try:
            rm_events = self.event_logs.get_raw_materials_used_events(
                product.product_id
            )
            transformation_events = self.event_logs.get_transformations_events(
                product.product_id
            )
        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
            return None
        else:
            # materials and transformation info is added to the product
            product.rawMaterials = [
                RawMaterial.from_event(event=ev) for ev in rm_events
            ]
            product.transformations = [
                Transformation.from_event(event=ev) for ev in transformation_events
            ]
            return product

    def get_all_raw_materials(self) -> List[RawMaterial]:
        """This function fetches and returns the list of all the raw materials
        saved on the blockchain

        Returns:
            `list[RawMaterial]`: a list of all the raw materials
        """
        try:
            rms = self.user_contract.functions.getRawMaterials().call()
        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
            return []
        except solidity_exceptions.ContractLogicError as error:
            print(error)
            return []
        else:
            return [RawMaterial.from_blockchain(rm) for rm in rms]

    def get_usable_raw_materials(self, transformer_address) -> List[RawMaterial]:
        """This function fetches and returns a list of non-used raw materials that belong
        to the current user from the blockchain
        Args:
            transformer_address(`ChecksumAddress`): the address of the current user
        Returns:
            `list[RawMaterial]`: a list of all the non-used raw materials
        """
        rms = list(
            filter(
                lambda raw_mat: not raw_mat.is_used
                and raw_mat.transformer_address == transformer_address,
                self.get_all_raw_materials(),
            )
        )
        return rms

    def get_all_products(self) -> List[Product]:
        """
        Retrieves all `Product`s on the blockchain.
        This function returns a list of all the products without information
        about raw materials used or transformations.

        If you need information for a specific product, use
        `get_product_details`, or if you need them for all products use
        `get_all_products_detailed`


        Returns:
            `list[Product]`: a list of all the products on the blockchain
        """
        try:
            products = self.user_contract.functions.getProducts().call()
        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
            return []
        else:
            return [Product.from_blockchain(product) for product in products]
