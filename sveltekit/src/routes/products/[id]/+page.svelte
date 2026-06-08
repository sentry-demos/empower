<script lang="ts">
	import { addToCart } from '$lib/cart.svelte';
	import Button from '$lib/components/Button.svelte';
	import Star from '$lib/components/icons/Star.svelte';
	import type { Product } from '$lib/types';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const product = $derived(data.product);

	function getRating(product: Product): number {
		return Number(
			(
				product.reviews.reduce((a, b) => a + (b['rating'] || 0), 0) / product.reviews.length
			).toFixed(1)
		);
	}
</script>

{#if product}
	<div class="mt-12 flex flex-row gap-8">
		<img class="max-w-1/2" src={product.img} alt="product image of {product.title}" />
		<div class="flex flex-col gap-4 border-t border-gray-500 pt-4">
			<h1 class="font-serif text-4xl font-semibold">{product.title}</h1>
			<p class="text-lg">{product.description}</p>
			<p>{product.descriptionfull}</p>
			<Button onclick={() => addToCart(product)}>Add to cart — ${product.price}.00</Button>
			{#if product.reviews?.length}
				<div class="flex flex-row items-center gap-2">
					<span class="text-lg font-bold">{product.reviews.length} Reviews:</span>
					<span class="inline-flex flex-row gap-1">
						{#each [1, 2, 3, 4, 5] as i}
							<Star fill={i <= getRating(product)} color="#FFD700" />
						{/each}
					</span>
				</div>
				{#each product.reviews as review}
					<p>{review.description}</p>
				{/each}
			{/if}
		</div>
	</div>
{:else}
	<div>Error</div>
{/if}
