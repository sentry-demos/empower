import type { Actions } from '@sveltejs/kit';

import * as Sentry from '@sentry/sveltekit';

export const actions: Actions = {
	default: async ({ request, fetch, locals }) => {
		Sentry.startSpan(
			{
				name: 'Submit Checkout Form',
				op: 'function.checkout'
			},
			async (span) => {
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

				const cart = {
					items: []
				};

				const response = await fetch(locals.backendUrl + '/checkout?v2=true', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						cart: cart,
						form: formValues,
						validate_inventory: checkout_success ? 'false' : 'true'
					})
				})
					.catch((err) => {
						checkout_span.setAttributes({
							'checkout.error': 1,
							status: 500
						});
						return { ok: false, status: 500 };
					})
					.then((res) => {
						stopMeasurement();
						return res;
					});

				return {
					success: true
				};
			}
		);
	}
};
