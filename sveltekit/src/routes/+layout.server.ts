export const load = async () => {
	return {
		backendUrl: process.env.SVELTEKIT_APP_FLASK_BACKEND
	};
};
