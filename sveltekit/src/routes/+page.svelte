<script lang="ts">
	import { onMount } from 'svelte';
	import * as Sentry from '@sentry/sveltekit';
	import ButtonLink from '../lib/components/ButtonLink.svelte';
	import type { PageData } from './$types';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	onMount(() => {
		console.log({ backendUrl: data.backendUrl });
		try {
			// This should be the only http request for home page, for health check purposes
			fetch(data.backendUrl + '/success', {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});
		} catch (err) {
			Sentry.captureException(err);
		}
	});
</script>

<div
	style="background-image: url(/plants-background-img.jpg); background-size: cover"
	class="absolute bottom-0 left-0 right-0 top-0"
></div>

<div class="sentry-unmask relative h-screen overflow-hidden">
	<div class="relative z-10 flex h-full flex-col items-start justify-center px-4 text-center">
		<h1 class="mb-4 font-serif text-5xl">Empower your plants</h1>
		<p class="mb-8 text-2xl">Keep your houseplants happy.</p>
		<ButtonLink to={'/products'}>Browse products</ButtonLink>
	</div>
</div>
