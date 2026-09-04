<script lang="ts">
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	function goBack() {
		window.history.back();
	}
</script>

<div class="min-h-screen p-8">
	<div class="mx-auto w-full max-w-3xl">
		<div class="mb-8">
			<button onclick={goBack} class="cursor-pointer text-[#002626] hover:underline">← Back</button>
		</div>
		{#if data.employee}
			<div class="flex items-center gap-8">
				<img
					src={data.employee.img}
					alt={data.employee.name}
					class="h-48 w-48 rounded-full object-cover shadow-lg"
				/>
				<div class="flex flex-col">
					<h1 class="mb-4 font-serif text-4xl">{data.employee.name}</h1>
					<p class="text-lg leading-relaxed">{data.employee.bio}</p>
				</div>
			</div>
		{:else}
			<div class="text-center">
				<h1 class="mb-4 font-serif text-4xl">Employee Not Found</h1>
				<p class="text-lg">Sorry, we couldn't find the employee you're looking for.</p>
			</div>
		{/if}
	</div>
</div>
