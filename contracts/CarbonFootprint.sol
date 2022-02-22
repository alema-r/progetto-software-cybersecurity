// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./ProductLibrary.sol";


/**
 * @title ERC721 contract to manage all products.
 * @notice Each product is actually an NFT.
 * @dev All functions should be called from the proxy contract `User`.
 */
contract CarbonFootprint is ERC721{
    // The address of the owner
    address public owner;

	// Variable that represent the id of a product
    uint256 private productId = 0;

    // Array that contains all products present in the contract.
    ProductLibrary.Product[] private allProducts;

    // Rivedere questo mapping nel caso in cui i prodotti possano avere lo stesso nome
    mapping(string => bool) private productExists;

    // Evento da emettere sulla blockchain quando viene aggiornata una carbon footprint
    /**
     * @notice Event used to track each carbon footprint addition.
     * @param userAddress The address of the user that adds the carbon footprint
     * @param cf The carbon footprint added.
     * @param pId The id of the updated product.
     */
	event newCFAdded(address userAddress, uint256 cf, uint256 pId);

    /**
     * @notice Initializes the contract and sets the `owner` to `msg.sender`.
     * @dev See {ERC721-constructor}
     */
	constructor() ERC721("CarbonFootprintMonitor", "CFM"){
        owner = msg.sender;
    }

    /**
     * @notice Returns all the products present in `allProducts`.
     * @return An array of `ProductLibrary.Product`.
     */
	function getAllProducts() public view returns (ProductLibrary.Product[] memory){
        return allProducts;
    }

    /**
     * @notice Returns the product with the specified `pId` id.
     * @dev Since `productId` is initialized to 0 and it is incremented by 1 
     * each time a new product is created, the id of a product matches 
     * the position in the `allProducts` array.
     * @param pId The id of the product.
     * @return A `ProductLibrary.Product` object.
     */
	function getProductById(uint256 pId) public view returns (ProductLibrary.Product memory){
        require(pId < productId, "Il prodotto non esiste");
        return allProducts[pId];
    }

    /**
     * @notice Creates a product with specified product name, raw material and initial carbon footprint.
     * Then it adds it to `allProducts` and emits a `newCFAddded` event.
     * @dev See {ERC721-_safeMint}
	 * @param _productName The name of the product.
	 * @param _rawMaterial The raw material used for the product.
	 * @param cf The initial carbon footprint.
     */
	function mintProduct(
		string calldata _productName, 
		string calldata _rawMaterial, 
		uint256 cf
	) 
		public 
	{
        require(bytes(_productName).length != 0, "Il nome del prodotto non e' valido.");
        require(bytes(_rawMaterial).length != 0, "Il nome della materia prima non e' valido.");
        require(!productExists[_productName], "Il prodotto e' gia' presente.");
        assert(!(_exists(productId)));
        _safeMint(tx.origin, productId);
        allProducts.push(ProductLibrary.Product(productId, _productName, _rawMaterial, tx.origin, cf, false));
        productExists[_productName] = true;
        emit newCFAdded(tx.origin, cf, productId);
        productId++;
    }

    /**
     * @notice Adds a carbon footprint to the specified product
     * @param partialCF The carbon footprint to be added.
     * @param pId The id of the product to be modified. 
     * @param isEnded Specify if this is the last transformation or not.
     */
	function addCF(uint256 partialCF, uint256 pId, bool isEnded) public{
        require(pId < productId, "Il prodotto non esiste");
        ProductLibrary.Product storage productToUpdate = allProducts[pId];
        require(productToUpdate.ended == false, "Il prodotto non e' piu' modificabile.");
        require(productToUpdate.currentOwner == tx.origin, "Per aggiungere una carbon footprint al prodotto devi esserne il proprietario.");
        productToUpdate.CF += partialCF;
        emit newCFAdded(tx.origin, partialCF, pId);
        if(isEnded){
            productToUpdate.ended = true;
        }
    }

    /**
     * @notice Transfer the property of a product with id `pId` to address `recipient`.
     * @dev Clients do not own any product so it's impossible for them to call this function.
     * The validity of the `recipient` address is checked by the `_safeTransfer` function. See
     * {ERC721-_safeTransfer}.
     * @param recipient The address to transfer the product property to
     * @param pId The id of the product to be transferred.
     */ 
	function transferProduct(address recipient, uint256 pId) public {
        require(pId < productId, "Il prodotto non esiste");
        ProductLibrary.Product storage productToUpdate = allProducts[pId];
        require(productToUpdate.ended == false, "Il prodotto non e' piu' modificabile.");
        _safeTransfer(tx.origin, recipient, pId, "");
        productToUpdate.currentOwner = recipient; 
    }
}
