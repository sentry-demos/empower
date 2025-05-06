<script lang="ts">
	import NavItem from './NavItem.svelte';

	import { route } from '$lib/ROUTES';

	import { cartState } from '$lib/cart.svelte';

	const cartTotal = $derived(
		cartState.reduce((acc, item) => acc + item.product.price * item.quantity, 0)
	);

	let { class: className } = $props();
</script>

<nav class="sticky top-0 z-10 flex flex-row items-center justify-center bg-white {className}">
	<div class="flex w-screen justify-between p-4 xl:w-[80vw]">
		<a href={route('/')} class="flex items-center gap-2 px-4">
			<img src="/logo192.png" alt="Empower Plant" class="h-10 w-10" />
			<span class="hidden gap-4 text-4xl font-light md:block">Empower Plant</span>
		</a>
		<div class="flex flex-row items-center gap-4 text-xl font-light">
			<NavItem href={route('/about')}>About</NavItem>
			<NavItem href={route('/products')}>Products</NavItem>
			<NavItem href={route('/cart')}
				>Cart

				{#if cartTotal > 0}
					<span class="font-light">(${cartTotal.toFixed(2)})</span>
				{/if}
			</NavItem>
		</div>
	</div>
</nav>
