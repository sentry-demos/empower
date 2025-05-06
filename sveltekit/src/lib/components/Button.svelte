<script lang="ts">
	let {
		children = undefined,
		class: className = undefined,
		id = undefined,
		onclick = undefined,
		type = 'button'
	} = $props();
</script>

<button
	{type}
	class="button w-fit cursor-pointer rounded bg-[#002626] px-4 py-2 font-bold text-white transition-colors hover:bg-[#dddc4e] hover:text-black active:bg-[#f6cfb2] {className}"
	{id}
	onclick={(evt) => {
		evt.preventDefault();
		onclick?.(evt);
	}}
>
	{@render children?.()}
</button>
