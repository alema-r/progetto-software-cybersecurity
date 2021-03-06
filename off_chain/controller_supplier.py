"""Module that implements a supplier controller class
"""
from requests import exceptions as requests_exceptions

from web3 import exceptions as solidity_exceptions

from off_chain.base_controller import BlockChain


class Supplier(BlockChain):
    """Controller class for a supplier"""

    def create_raw_materials_on_blockchain(self, raw_materials) -> bool:
        """Functions that inserts a new raw materials on the blockchain

        Args:
            raw_materials (`list[RawMaterial]`): List of raw materials that must be inserted
        """
        rm_name_list = []
        rm_lot_list = []
        rm_cf_list = []
        rm_tr_list = []
        for raw_mat in raw_materials:
            rm_name_list.append(raw_mat.name)
            rm_lot_list.append(raw_mat.lot)
            rm_cf_list.append(raw_mat.cf)
            rm_tr_list.append(raw_mat.transformer_address)
        try:
            tx_hash = self.user_contract.functions.createRawMaterials(
                rm_name_list,
                rm_lot_list,
                rm_cf_list,
                rm_tr_list,
            ).transact()
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
            return True

        except requests_exceptions.ConnectionError:
            print("Could not connect to the blockchain. Try again")
            return False

        except solidity_exceptions.ContractLogicError as error:
            print(error)
            return False

        except solidity_exceptions.ValidationError:
            print("Insertion of raw materials failed. Please insert raw materials again")
            return False