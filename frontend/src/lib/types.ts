export interface Attribute {
  attribute: {
    type: string;
    value: string;
  };
}

export interface Variant {
  id: number;
  sku: string;
  price: number;
  stock: number;
  attributes: Attribute[];
}

export interface Image {
  id: number;
  url: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  children: Category[];
}

export interface SubCategory {
  name: string;
  slug: string;
}

export interface Brand {
  name: string;
  slug: string;
}

export type Product = {
  id: number;
  name: string;
  description: string;
  category: Category;
  brand: Brand;
  images: Image[];
  variants: Variant[];
};

export type CartItem = {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image: string;
  size: string;
}; 