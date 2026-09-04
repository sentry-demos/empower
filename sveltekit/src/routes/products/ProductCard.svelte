<script lang="ts">
	import { addToCart } from '$lib/cart.svelte';
	import Button from '$lib/components/Button.svelte';
	import Star from '$lib/components/icons/Star.svelte';
	import { route } from '$lib/ROUTES';
	import type { Product } from '$lib/types';

	let { product, rating } = $props();

	function addProductToCart(product: Product) {
		addToCart(product);
	}
</script>

<li
	class="m-4 cursor-pointer rounded-lg bg-white shadow-md transition-all hover:scale-[102%] hover:shadow-md"
>
	<a href={route('/products/[id]', { id: product.id })} class="flex flex-col gap-2 p-4">
		<img
			src={product.img}
			alt="product image of {product.title}"
			class="sentry-block h-auto w-full rounded-lg object-cover"
		/>
		<div class="flex flex-col gap-1">
			<h2 class="font-serif text-2xl font-semibold">{product.title}</h2>
			<p class="text-gray-600">{product.description}</p>
		</div>
		<Button id="addToCart" onclick={() => addProductToCart(product)}>
			<span class="sentry-unmask">Add to cart — $</span>
			{product.price}.00
		</Button>
		<p class="inline-flex flex-row items-center gap-2 text-sm text-gray-500">
			<span class="inline-flex flex-row gap-1">
				{#each [1, 2, 3, 4, 5] as i}
					<Star fill={i <= rating} color="#FFD700" />
				{/each}
			</span>
			<span class="text-md">
				({product.reviews.length})
			</span>
		</p>
	</a>
</li>
