export default function countItemsInCart(cart) {
    console.log("countItemsInCart called with:", cart);
    let totalItems = 0;
    
    if (!cart || !cart.quantities) {
        console.log("Cart or cart.quantities is undefined!");
        return totalItems;
    }

    console.log("Cart quantities object:", cart.quantities);
    console.log("Object.values(cart.quantities):", Object.values(cart.quantities));
    
    totalItems = Object.values(cart.quantities)
        .reduce((sum, quantity) => {
            console.log("Adding quantity:", quantity);
            return sum + quantity;
        }, 0);

    console.log("Final total:", totalItems);
    return totalItems;
}