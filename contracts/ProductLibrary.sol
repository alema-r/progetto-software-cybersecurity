// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.0 <0.9.0;

/**
 * @title A library that contains a struct representing a product.
 */
library ProductLibrary{
    
	// Struct that represent a product
    struct Product {
        uint256 productId;
        string name;
        address currentOwner;
        uint256 CF;
        bool ended;
    }
    // Struct that represent rawmaterial
    struct RawMaterial {
        string name;
        uint256 lot;
        uint256 RmId;
    }

}
