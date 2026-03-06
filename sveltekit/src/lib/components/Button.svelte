<script lang="ts">
	interface Props {
		onclick?: (evt: Event) => void;
		class?: string;
		id?: string;
		type?: 'button' | 'submit';
		children?: import('svelte').Snippet;
	}

	let {
		children = undefined,
		class: className = undefined,
		id = undefined,
		onclick = undefined,
		type = 'button'
	}: Props = $props();
</script>

<button
	{type}
	class="button w-fit cursor-pointer rounded bg-[#002626] px-4 py-2 font-bold text-white transition-colors hover:bg-[#dddc4e] hover:text-black active:bg-[#f6cfb2] {className}"
	{id}
	onclick={(evt) => {
		if (type !== 'submit') {
			evt.preventDefault();
		}
		onclick?.(evt);
	}}
>
	{@render children?.()}
</button>
