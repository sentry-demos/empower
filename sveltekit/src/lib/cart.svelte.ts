import type { Product } from '$lib/types';

export type CartItem = {
	product: Product;
	quantity: number;
};

export const cartState = $state<CartItem[]>([]);

export function addToCart(product: Product) {
	const item = cartState.find((item) => item.product.id === product.id);
	if (item) {
		item.quantity++;
	} else {
		cartState.push({ product, quantity: 1 });
	}
}

export function removeFromCart(product: Product) {
	const item = cartState.find((item) => item.product.id === product.id);
	if (item) {
		item.quantity--;
	}
}
