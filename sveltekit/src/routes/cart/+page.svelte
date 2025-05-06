<script lang="ts">
	import { addToCart, removeFromCart } from '$lib/cart.svelte';
	import Button from '$lib/components/Button.svelte';
	import ButtonLink from '$lib/components/ButtonLink.svelte';
	import { route } from '$lib/ROUTES';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	const cartState = $derived(data.cartState);
</script>

<div class="mt-8 flex w-full flex-col items-center justify-center border-b pb-4">
	<h1 class="font-serif text-3xl font-semibold">Cart</h1>
</div>

<div class="mt-4 flex w-full flex-col items-center justify-center">
	{#if cartState.length === 0}
		<div>Add some items to your cart :&#41;</div>
	{:else}
		<table class="w-full">
			<tbody>
				{#each cartState as item}
					<tr class="border-b">
						<td class="w-24 p-4">
							<img
								src={item.product.imgcropped}
								alt={item.product.title}
								class="h-16 w-auto rounded"
							/>
						</td>

						<td class="w-fit p-4 font-serif text-2xl">{item.product.title}</td>

						<td class="p-4 text-left">$ {item.product.price.toFixed(2)}</td>

						<td class="">
							<Button class="p-4 text-right" onclick={() => removeFromCart(item.product)}>-</Button>
							<span class="p-4 text-right">{item.quantity}</span>
							<Button class="p-4 text-right" onclick={() => addToCart(item.product)}>+</Button>
						</td>

						<td class="p-4 text-left">$ {(item.product.price * item.quantity).toFixed(2)}</td>
					</tr>
				{/each}
			</tbody>
		</table>

		<p class="mt-4 font-serif text-2xl font-bold">
			Cart Subtotal: $ {cartState
				.reduce((acc, item) => acc + item.product.price * item.quantity, 0)
				.toFixed(2)}
		</p>

		<ButtonLink to={route('/checkout')}>Proceed to Checkout</ButtonLink>
	{/if}
</div>
