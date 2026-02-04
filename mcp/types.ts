export interface PlantProduct {
  id: number;
  title: string;
  description: string;
  descriptionfull: string;
  price: number;
  img: string;
  imgcropped: string;
  reviews: Array<{
    id: number;
    productid: number;
    rating: number;
    customerid: number | null;
    description: string | null;
    created: string;
    pg_sleep: string;
  }>;
}

export interface PlantProductSummary {
  id: number;
  title: string;
  description: string;
  price: number;
}

export interface PlantCareGuide {
  plantName: string;
  difficulty: string;
  sunlight: string;
  watering: {
    frequency: string;
    amount: string;
    tips: string;
  };
  soil: {
    type: string;
    drainage: string;
    ph: string;
  };
  temperature: {
    ideal: string;
    minimum: string;
    maximum: string;
  };
  humidity: string;
  fertilizer: {
    type: string;
    frequency: string;
    season: string;
  };
  commonIssues: Array<{
    problem: string;
    cause: string;
    solution: string;
  }>;
  propagation: string;
  toxicity: string;
}

export interface CheckoutItem extends PlantProduct {}

export interface CheckoutCart {
  items: CheckoutItem[];
  quantities: Record<string, number>;
  total: number;
}

export interface CheckoutForm {
  email: string;
  subscribe: string;
  firstName: string;
  lastName: string;
  address: string;
  city: string;
  country: string;
  state: string;
  zipCode: string;
}

export interface CheckoutRequest {
  cart: CheckoutCart;
  form: CheckoutForm;
  validate_inventory: string;
}
