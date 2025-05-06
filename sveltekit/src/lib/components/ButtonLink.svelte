<script lang="ts">
	export let to: string;
</script>

<a href={to} class="button-link">
	<slot />
</a>

<style>
	.button-link {
		display: inline-block;
		padding: 0.75rem 1.5rem;
		background-color: #4caf50;
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
