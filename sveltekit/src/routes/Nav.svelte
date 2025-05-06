<script lang="ts">
	import NavItem from './NavItem.svelte';

	import { route } from '$lib/ROUTES';

	import { page } from '$app/state';

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
			<NavItem href={route('/cart')}>Cart</NavItem>
		</div>
	</div>
</nav>
