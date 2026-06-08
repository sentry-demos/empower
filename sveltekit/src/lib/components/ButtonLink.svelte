<script lang="ts">
	interface Props {
		to: string;
		children?: import('svelte').Snippet;
	}

	let { to, children }: Props = $props();
</script>

<a href={to} class="button-link">
	{@render children?.()}
</a>

<style>
	.button-link {
		display: inline-block;
		padding: 0.75rem 1.5rem;
		background-color: #002626;
		color: white;
		text-decoration: none;
		border-radius: 4px;
		font-weight: bold;
		transition: background-color 0.3s ease;
	}

	.button-link:hover {
		background-color: #45a049;
	}
</style>
