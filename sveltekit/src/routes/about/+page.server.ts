import type { PageServerLoad } from './$types';
import type { Employee } from '../../lib/data/employees/types';
import Jane from '../../lib/data/employees/jane';
import Lily from '../../lib/data/employees/lily';
import Keith from '../../lib/data/employees/keith';
import Mason from '../../lib/data/employees/mason';
import Emma from '../../lib/data/employees/emma';
import Noah from '../../lib/data/employees/noah';

const employees: Employee[] = [Jane, Lily, Keith, Mason, Emma, Noah];

export const load: PageServerLoad = async () => {
	// Simulate a small delay to emulate network latency
	await new Promise((resolve) => setTimeout(resolve, 500));
	return {
		employees
	};
};
