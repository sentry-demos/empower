export type Product = {
	id: number;
	title: string;
	description: string;
	descriptionfull: string;
	price: number;
	img: string;
	imgcropped: string;
	reviews: Review[];
};

export type Review = {
	id: number;
	productid: number;
	rating: number;
	customerid: number | null;
	description: string | null;
	created: string;
	pg_sleep: string;
};
