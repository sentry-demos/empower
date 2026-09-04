export function countItemsInCart(cart) {
    let totalItems = 0;
    
    if (!cart || !cart.quantities) {
        console.log("Cart or cart.quantities is undefined!");
        return totalItems;
    }

    totalItems = Object.values(cart.quantities)
        .reduce((sum, quantity) => {
            console.log("Adding quantity: ", quantity);
            console.log("Total cart size: ", (sum + quantity));
            return sum + quantity;
        }, 0);

    return totalItems;
}