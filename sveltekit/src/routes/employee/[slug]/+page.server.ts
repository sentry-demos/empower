import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params }) => {
	try {
		const employee = await import(`$lib/data/employees/${params.slug}.ts`);
		return {
			employee: employee.default
		};
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
	} catch (e: unknown) {
		error(404, 'Employee not found');
	}
};
