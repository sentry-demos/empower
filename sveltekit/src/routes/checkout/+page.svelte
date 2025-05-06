<script lang="ts">
	import Button from '$lib/components/Button.svelte';
	import { route } from '$lib/ROUTES';
</script>

<div class="mt-8 flex w-full flex-col items-center justify-center border-b pb-4">
	<h1 class="font-serif text-3xl font-semibold">Checkout</h1>
</div>
<div class="mt-4 flex w-full flex-col items-center justify-center">
	<form class="mb-8 w-full max-w-md">
		<h3 class="mb-4 font-serif text-2xl font-medium">Contact Information</h3>
		<div class="mb-4">
			<label for="email" class="mb-2 block font-medium">Email</label>
			<input
				type="email"
				id="email"
				name="email"
				class="w-full rounded border p-2"
				required
				value="plant.lover@example.com"
			/>

			<div class="mt-2 flex flex-row items-center gap-2">
				<input type="checkbox" id="email-optin" name="email-optin" />
				<label for="email-optin" class="block align-bottom font-medium"
					>Keep me updated with new sales and products</label
				>
			</div>
		</div>
		<h3 class="mb-4 font-serif text-2xl font-medium">Shipping Address</h3>
		<div class="mb-4">
			<label for="firstName" class="mb-2 block font-bold">First Name</label>
			<input
				type="text"
				id="firstName"
				name="firstName"
				class="w-full rounded border p-2"
				value="Jane"
				required
			/>
		</div>
		<div class="mb-4">
			<label for="lastName" class="mb-2 block font-bold">Last Name</label>
			<input
				type="text"
				id="lastName"
				name="lastName"
				class="w-full rounded border p-2"
				value="Greenthumb"
				required
			/>
		</div>
		<div class="mb-4">
			<label for="address" class="mb-2 block font-bold">Address</label>
			<input
				type="text"
				id="address"
				name="address"
				class="w-full rounded border p-2"
				value="123 Main Street"
				required
			/>
		</div>
		<div class="mb-4">
			<label for="city" class="mb-2 block font-bold">City</label>
			<input
				type="text"
				id="city"
				name="city"
				class="w-full rounded border p-2"
				value="San Francisco"
				required
			/>
		</div>
		<div class="mb-4">
			<label for="state" class="mb-2 block font-bold">State</label>
			<input
				type="text"
				id="state"
				name="state"
				class="w-full rounded border p-2"
				value="CA"
				required
			/>
		</div>
		<div class="mb-4">
			<label for="zip" class="mb-2 block font-bold">Zip</label>
			<input
				type="text"
				id="zip"
				name="zip"
				class="w-full rounded border p-2"
				value="94101"
				required
			/>
		</div>

		<Button type="submit" class="w-full">Submit</Button>
	</form>
	<a href={route('/cart')} class="mb-20 underline">Back to Cart</a>
</div>
