<script lang="ts">
	import { route } from '$lib/ROUTES';
	import { page } from '$app/state';

	let { href, children } = $props();

	let currentRoute = $derived(page.route.id);
</script>

<a
	href={route(href)}
	class="border-b-2 hover:border-gray-300 {currentRoute === href
		? 'border-gray-300'
		: 'border-transparent'}"
>
	{@render children()}
</a>
