export const viewport = {
  themeColor: '#000000',
};

export const metadata = {
  title: 'App Monitoring',
  description: 'Web site created with Next.js.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        {/*
                        This HTML file is a template.
                        If you open it directly in the browser, you will see an empty page.

                        You can add webfonts, meta tags, or analytics to this file.
                        The build step will place the bundled scripts into the <body> tag.

                        To begin the development, run `npm start` or `yarn start`.
                        To create a production bundle, use `npm run build` or `yarn build`.
                    */}
      </body>
    </html>
  );
}
