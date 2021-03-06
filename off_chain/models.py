"""Module that implements models for solidity data structures
"""
from eth_typing import ChecksumAddress
from tabulate import tabulate
from web3.datastructures import AttributeDict


class RawMaterial:
    """
    Class mapping the structure of a raw material on the blockchain
    """

    def __init__(
        self,
        name: str,
        lot: int,
        address,
        cf: int,
        is_used=False,
        material_id: int = None,
        transformer_address: ChecksumAddress = None,
    ):
        self.material_id = material_id
        self.name = name
        self.lot = lot
        self.address = address
        self.cf = cf
        self.is_used = is_used
        self.transformer_address = transformer_address

    @classmethod
    def from_blockchain(cls, data: tuple):
        """
        Alternative constructor of RawMaterial class in order to
        simply instantiate objects with data retrieved from blockchain
        Args:
            data: (tuple) structure returned after calling smart contracts

        Returns:
            RawMaterial Object
        """
        return cls(data[1], data[2], data[3], data[5], data[6], data[0], data[4])

    @classmethod
    def from_event(cls, event: AttributeDict, used=False):
        """
        Alternative constructor of RawMaterial class in order to
        simply instantiate objects with data about events retrieved from blockchain
        Args:
            event: (AttributeDict) dictionary containing event logs returned from blockchain
            used: (bool) boolean parameter indicating whether raw material is used or not

        Returns:
            RawMaterial Object
        """
        return cls(
            event.args.name, event.args.lot, event.args.supplier, event.args.cf, used
        )

    def __str__(self):
        if len(self.name) <= 25:
            length = len(self.name)
            # padding = "".join([" " for i in range(length, 30)])
            padding = " " * (30 - length)
            name = self.name + padding
        else:
            name = self.name[:22] + "..." + " " * 5
        if len(str(self.lot)) <= 6:
            # padding = "".join([" " for i in range(len(str(self.lot)), 11)])
            padding = " " * (11 - len(str(self.lot)))
            lot = str(self.lot) + padding
        else:
            # padding = "".join([" " for i in range(0, 5)])
            padding = " " * 5
            lot = str(self.lot) + padding
        if len(str(self.cf)) < 6:
            # padding = "".join([" " for i in range(len(str(self.cf)), 11)])
            padding = " " * (11 - len(str(self.cf)))
            cf = str(self.cf) + padding
        else:
            # padding = "".join([" " for i in range(0, 5)])
            padding = " " * 5
            cf = str(self.cf) + padding
        return f"{name}{lot}{cf}{self.address}{self.transformer_address}"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, RawMaterial):
            return (
                self.name == __o.name
                and self.lot == __o.lot
                and self.address == __o.address
            )
        else:
            return False


class Product:
    """
    Class mapping the structure of a product on the blockchain
    """

    def __init__(
        self, name: str, address, cf: int, is_ended=False, product_id: int = None
    ):
        self.product_id = product_id
        self.name = name
        self.address = address
        self.cf = cf
        self.is_ended = is_ended
        self.transformations = []
        self.rawMaterials = []

    @classmethod
    def from_blockchain(cls, data: tuple):
        """
        Alternative constructor of Product class in order to
        simply instantiate objects with data retrieved from blockchain
        Args:
            data: (tuple) structure returned after calling smart contracts
        Returns:
            Product Object
        """
        return cls(data[1], data[2], data[3], data[4], data[0])

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Product):
            return self.product_id == __o.product_id
        else:
            return False

    def __str__(self):
        raw_materials_printable = [
            [
                raw.name[:22] + "..." if len(raw.name) > 25 else raw.name,
                raw.lot,
                raw.cf,
                raw.address,
            ]
            for raw in self.rawMaterials
        ]
        table_raw_materials = tabulate(
            raw_materials_printable,
            headers=["Name", "Lot", "Carbon Footprint", "Supplier"],
            tablefmt="tsv",
        )
        transformations_printable = [
            [t.cf, t.transformer] for t in self.transformations
        ]
        table_transformation = tabulate(
            transformations_printable,
            headers=["Carbon Footprint", "Transformer"],
            tablefmt="tsv",
        )
        s = (
            f"Information about product No. {self.product_id}\nOwner: {self.address}\n"
            + f"Name:{self.name}, Actual Carbon Footprint:{self.cf}\n"
            + "These are raw materials used for this product:\n\n"
            + table_raw_materials
            + f"\n\n{'-'*78}\n\n"
            + "These are transformation done on this product:\n"
            + table_transformation
            + f"\n\n{'-'*78}\n\n"
        )
        s += (
            "Product is finished\n"
            if self.is_ended
            else "Product is still in the works\n"
        )
        return s


class Transformation:
    """
    Class mapping the structure of a transformation operation recorded on a blockchain
    """

    def __init__(self, transformer, cf):
        self.transformer = transformer
        self.cf = cf

    @classmethod
    def from_event(cls, event: AttributeDict):
        """
        Alternative constructor of Transformation class in order to simply
        instantiate objects with data about events retrieved from blockchain
        Args:
            event: (AttributeDict) dictionary containing event logs returned from blockchain

        Returns:
            RawMaterial Object
        """
        return cls(event.args.userAddress, event.args.cf)

    def __str__(self):
        return f"{self.cf}\t{self.transformer}"
