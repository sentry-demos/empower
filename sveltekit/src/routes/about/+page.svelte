<script lang="ts">
	import type { PageData } from './$types';
	import { route } from '$lib/ROUTES';

	let { data }: { data: PageData } = $props();
</script>

<div class="mt-8 p-8">
	<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
		<div>
			<h1 class="mb-6 font-serif text-6xl">About us</h1>
			<p class="mb-4 leading-relaxed">
				Empower Plant is an IoT company determined to keep house plants happy. After reading Michael
				Pollan's 2013 New Yorker article ("The Intelligent Plant"), the wife-and-wife founding team
				invested their life savings in measuring and improving the emotional state of their leafy
				housemates. Seven years later, the company's grown from its humble roots in the couples'
				backyard greenhouse (converted from a garage) into a Series C-funded San Francisco startup
				and the world's most accurate plant mood measurer ("a must-have for any responsible plant
				parent," according to Plant Parenthood Magazine). Their original state-of-the-art product is
				a technological marvel built with a plant-first mindset, and they now offer a range of
				plant-centric options.
			</p>
			<p class="mb-4 leading-relaxed">
				Today, the company employs 170 people (and 852 plants) in San Francisco, New York City,
				Denver, and Kiev.
			</p>
		</div>
		<div>
			<ul class="grid grid-cols-2 gap-8">
				{#each data.employees as employee}
					<li class="flex flex-col items-center justify-center">
						<a
							href={route('/employee/[slug]', { slug: employee.url })}
							class="block transition-opacity hover:opacity-80"
						>
							<img
								src={employee.img}
								alt={employee.name}
								class="mx-auto mb-2 h-52 w-52 rounded-full object-cover shadow-md"
							/>
							<h5 class="text-center text-sm font-medium">
								{employee.name}
							</h5>
						</a>
					</li>
				{/each}
			</ul>
		</div>
	</div>
</div>
