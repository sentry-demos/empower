import type { Product } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load = (async ({ parent, fetch }) => {
	const { backendUrl } = await parent();

	console.log(backendUrl);

	const productResponse = fetch(`${backendUrl}/products`).then((res) => res.json()) as Promise<
		Product[]
	>;

	return {
		productResponse
	};
}) satisfies PageServerLoad;
