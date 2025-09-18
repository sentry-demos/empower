## About
This is the Server Side Rendered Next.js version of the empower app, powered by the Next.js app router and Vercel Postgres
## Usage
* The produciton Vecel deployment of the app can be found at https://nextjs.empower-plant.com/
* To run the app locally, [install vercel cli](https://vercel.com/docs/cli), then use the `vercel dev` comman from within the empower directory
    * if prompted to sign in, use `SAML Single Sign-On` option and enter `sentry` as slug.
* Error events are routed to the nextjs project within the empower demo org
* The error workflow is the same as the react app:
    * To trigger the Slow DB Query and N + 1 perforamnce issues, visit the /products route. 
    * To trigger the checkout error, follow the usual checkout workflow. Instead of making a call to an external service, the inventory logic is handled by the checkout server action

