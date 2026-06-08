import type { Product } from '$lib/types';
import type { PageLoad } from './$types';

export const load = (async ({ fetch, parent, params }) => {
	const { backendUrl } = await parent();

	const req = await fetch(`${backendUrl}/products-join`);

	const data = (await req.json()) as Product[];

	const numberedId = Number(params.id);

	const product = data.find((product) => product.id === numberedId);

	return { product };
}) satisfies PageLoad;
