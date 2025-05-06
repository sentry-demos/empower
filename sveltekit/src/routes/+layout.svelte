<script lang="ts">
	import Nav from './Nav.svelte';

	import '../app.css';

	let { children } = $props();
</script>

<Nav></Nav>
<main class="flex w-screen flex-row justify-center">
	<div class="flex w-full flex-col items-start xl:w-[80vw]">
		{@render children()}
	</div>
</main>
