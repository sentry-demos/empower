<script lang="ts">
	import LoadingIndicator from './LoadingIndicator.svelte';

	import type { PageData } from './$types';
	import ProductCard from './ProductCard.svelte';
	import type { Product } from '$lib/types';

	let { data }: { data: PageData } = $props();

	const productsResponse = $derived(data.productResponse);

	function getRating(product: Product) {
		return (
			product.reviews.reduce((a, b) => a + (b['rating'] || 0), 0) / product.reviews.length
		).toFixed(1);
	}
</script>

{#await productsResponse}
	<LoadingIndicator />
{:then products}
	<ul class="grid grid-cols-2 gap-4">
		{#each products as product}
			<ProductCard {product} rating={getRating(product)} />
		{/each}
	</ul>
{/await}
