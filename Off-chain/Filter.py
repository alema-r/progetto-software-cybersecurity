import operator
from tabulate import tabulate
import inquirer     #TEST
import BlockChain   #TEST
import event_logs   #TEST
import Transformer  #TEST
from web3 import Web3 #TEST
from Utils import carbon_fp_input_validation #TEST
from Supplier import raw_material_name_input_validation #TEST


def simpleFilter(result: list, criteria: dict) -> list:
    elements = criteria["elements"]()
    if criteria["event"]:
        for e in elements:
            if criteria["operator"](e["args"][criteria["field"]], criteria["value"]):
                result.append(e["args"]["pId"])
    else:
        for e in elements:
            if criteria["operator"](getattr(e, criteria["field"]), criteria["value"]):
                result.append(e.productId)
    return result


def orFilter(result, criteria):
    simpleFilter(result, criteria)
    return list(set(result))


def andFilter(result, criteria):
    temp = simpleFilter([], criteria)
    temp2 = result.copy()
    for e in temp2:
        if e not in temp:
            result.remove(e)
    return result

''''''

def id_input_validation(answers, current):
    """Functions that validates product's id

    Args:
        answers (Dictionary): Dictionary of given answers
        current (Dictionary): Current given answer

    Raises:
        inquirer.errors.ValidationError: Raised if the id's value isn't an integer
        inquirer.errors.ValidationError: Raised if id's value isn't greater than 0

    Returns:
        Boolean: True if the input is valid
    """
    try:
        int_id=int(current)
    except:
        raise inquirer.errors.ValidationError('', reason = 'Invalid input: ID must be an integer greater than 0')
    if int_id < 1:
        raise inquirer.errors.ValidationError('', reason = 'Invalid input: ID must be an integer greater than 0')
    return True

def address_validation(answers, current):
    """Functions that validates an address

    Args:
        answers (Dictionary): Dictionary of given answers
        current (Dictionary): Current given answer

    Raises:
        inquirer.errors.ValidationError: Raised if the address value is not a valid EIP55 checksummed address

    Returns:
        Boolean: True if the input is valid
    """
    return Web3.isAddress(current) # per il controllo ruolo mappare la getRole con una funzione su blockchain


def print_products(ids):
    products_printable = []
    for id in ids:
        p = BlockChain.get_product(id)
        products_printable.append([p.productId, p.name, p.address, p.CF, p.isEnded])

    #products = BlockChain.get_all_products()
    #products_printable = [[p.productId, p.name, p.address, p.CF, p.isEnded] for p in products]

    table = tabulate(products_printable, headers=["Id", "Name", "Owner", "CF", "isEnded"], tablefmt="tsv")
    print(table)

'''
def print_all_products():
    products = BlockChain.get_all_products()
'''

def detailed_print(id):
    product = BlockChain.get_product_details(id)
    product.__str__()


def select_operator():
    choices = ["Equal", "Greater", "Greater equal", "Lower", "Lower equal"]
    action = inquirer.list_input(
        message="Select an operator",
        choices=choices
    )
    if action == choices[0]:    #ALTRI OPERATORI
        op = operator.eq
    elif action == choices[1]:
        op = operator.gt
    elif action == choices[2]:
        op = operator.ge
    elif action == choices[3]:
        op = operator.lt
    elif action == choices[4]:
        op = operator.le
    return op


# DAVIDE LA FUNZIONE MI SONO ACCORTO CHE È RICORSIVA. HAI VERIFICATO SE LA RICORSIONE È TAIL E FATTA IN MANIERA
# INTELLIGENTE?
def filterProducts(results=[], filters=simpleFilter):
    criteria = {}
    choices = ["Id", "Name", "Owner", "CF", "Ended", "Supplier", "Transformer",
               "Raw Material"]
    action = inquirer.list_input(
        message="Select a field",
        choices=choices
    )
    if action == choices[0]:  # ID
        op = select_operator()
        value = int(inquirer.text(
            message="ID: ",
            validate=id_input_validation
        ))
        criteria = {"elements": BlockChain.get_all_products, "value": value, "field": "productId", "operator": op,
                    "event": False}
    elif action == choices[1]:  # NAME
        value = inquirer.text(
            message="Name: ",
            validate=Transformer.new_product_name_input_validation
        )
        criteria = {"elements": BlockChain.get_all_products, "value": value, "field": "name", "operator": operator.eq,  #OPERATOR CONTAINS?
                    "event": False}
    elif action == choices[2]:  # OWNER
        value = inquirer.text(
            message="Owner's address: ",
            validate=address_validation  # Controllo ruolo?
        )
        criteria = {"elements": BlockChain.get_all_products, "value": Web3.toChecksumAddress(value), "field": "address",
                    "operator": operator.eq, "event": False}
    elif action == choices[3]:  # CF
        op = select_operator()
        value = int(inquirer.text(
            message="CF value: ",
            validate=carbon_fp_input_validation
        ))
        criteria = {"elements": BlockChain.get_all_products, "value": value, "field": "CF", "operator": op,
                    "event": False}
    elif action == choices[4]:  # ISENDED
        choices = [("Yes", True), ("No", False)]
        action = inquirer.list_input(
            message="Is it ended?",
            choices=choices
        )
        criteria = {"elements": BlockChain.get_all_products, "value": action, "field": "isEnded",
                    "operator": operator.eq, "event": False}
    elif action == choices[5]:  # SUPPLIERS
        value = inquirer.text(
            message="Supplier's address: ",
            validate=address_validation  # controllo ruolo supplier?
        )
        criteria = {"elements": event_logs.get_raw_materials_used_events, "value": value, "field": "supplier",
                    "operator": operator.eq, "event": True}
    elif action == choices[6]:  # TRANSFORMERS
        value = inquirer.text(
            message="Transformer's address: ",
            validate=address_validation  # controllo ruolo transformer?
        )
        criteria = {"elements": event_logs.get_raw_materials_used_events, "value": value, "field": "transformer",
                    "operator": operator.eq, "event": True}
    elif action == choices[7]:  # RAWMATERIALNAME
        value = inquirer.text(
            message="Raw Material name: ",
            validate=raw_material_name_input_validation
        )
        criteria = {"elements": event_logs.get_raw_materials_used_events, "value": value, "field": "name",              #OPERATOR CONTAINS?
                    "operator": operator.eq, "event": True}

    results = filters(results, criteria)
    if len(results) > 0:
        print_products(results)
    choices = ["View one product details", "Add another filter", "Exit"]
    action = inquirer.list_input(
        message="",
        choices=choices
    )
    if action == choices[0]:
        value = int(inquirer.text(
            message="ID: ",
            validate=id_input_validation
        ))
        detailed_print(value)  # FUNZIONE DI PRINT DETTAGLIATA
    elif action == choices[1]:
        choices = ["AND", "OR"]
        action = inquirer.list_input(
            message="Filter Logic: ",
            choices=choices
        )
        if action == choices[0]:
            filterProducts(results, andFilter)
        else:
            filterProducts(results, orFilter)
