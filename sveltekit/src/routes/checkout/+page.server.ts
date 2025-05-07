import { error, redirect, type Actions } from '@sveltejs/kit';

import * as Sentry from '@sentry/sveltekit';
import type { CartItem } from '$lib/cart.svelte';

export const actions: Actions = {
	default: async ({ request, fetch, locals }) => {
		// Sentry.startSpan(
		// 	{
		// 		name: 'Submit Checkout Form',
		// 		op: 'function.checkout'
		// 	},
		// 	async () => {
		const formData = await request.formData();
		console.log({ formData, backend: locals.backendUrl });

		const formValues = {
			email: formData.get('email'),
			subscribe: formData.get('email-optin'),
			firstName: formData.get('firstName'),
			lastName: formData.get('lastName'),
			address: formData.get('address'),
			city: formData.get('city'),
			state: formData.get('state'),
			zip: formData.get('zip')
		};

		const rawCart = JSON.parse(formData.get('cart') as string) as CartItem[];

		console.log({ rawCart });

		const cart = {
			items: rawCart.map((r) => r.product),
			quantities: rawCart.reduce(
				(acc, r) => {
					acc[r.product.id] = r.quantity;
					return acc;
				},
				{} as Record<string, number>
			)
		};

		try {
			const response = await fetch(locals.backendUrl + '/checkout?v2=true', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					cart: cart,
					form: formValues,
					validate_inventory: 'true'
				})
			});

			console.log({ response });

			if (!response.ok) {
				error(500, 'Failed to checkout');
			}
		} catch (_) {
			Sentry.captureException(new Error('Failed to checkout'));
			error(500, 'Failed to checkout with throw');
			redirect(301, '/');
		}

		return {
			success: true
		};
	}
	// );
	// }
};
