<script lang="ts">
	import { route } from '$lib/ROUTES';
</script>

<nav class="sticky top-0 z-10 flex w-screen flex-row items-center justify-center bg-white">
	<div class="flex w-screen justify-between p-4 xl:w-[80vw]">
		<a href={route('/')} class="flex items-center gap-2 px-4">
			<img src="/logo192.png" alt="Empower Plant" class="h-10 w-10" />
			<span class="hidden gap-4 text-4xl font-light md:block">Empower Plant</span>
		</a>
		<div class="flex flex-row items-center gap-4 text-xl font-light">
			<a href={route('/about')} class="border-b-2 border-transparent hover:border-gray-300">About</a
			>
			<a href={route('/products')} class="border-b-2 border-transparent hover:border-gray-300"
				>Products</a
			>
			<a href={route('/cart')} class="border-b-2 border-transparent hover:border-gray-300"
				>Contact</a
			>
		</div>
	</div>
</nav>
