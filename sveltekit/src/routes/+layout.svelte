<script lang="ts">
	import Nav from './Nav.svelte';

	import '../app.css';

	let { children } = $props();
</script>

<Nav class="layoutWidth" />
<main class="layoutWidth flex flex-row justify-center">
	<div class="flex w-full flex-col items-start xl:w-[80vw]">
		{@render children()}
	</div>
</main>

<style>
	.layoutWidth {
		max-width: calc(100vw - 30px);
	}
</style>
