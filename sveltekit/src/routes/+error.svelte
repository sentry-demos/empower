<script lang="ts">
	import { page } from '$app/state';
	import Button from '$lib/components/Button.svelte';
</script>

<div class="mt-8 flex h-full w-full flex-col items-center justify-center gap-8">
	<h1 class="font-serif text-4xl">Well this is embarassing...</h1>

	<p>{page.status}: {page.error?.message}</p>

	<p class="max-w-md text-center">
		We were unable to process your order but will do everything we can to make it right. Please
		reach out to us if you have been charged or have any questions.
	</p>

	<Button>Contact Us</Button>
</div>
