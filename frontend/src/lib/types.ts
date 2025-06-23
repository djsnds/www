export interface BackendAttribute {
  id: number;
  type: string;
  value: string;
}

export interface VariantAttribute {
  attribute: BackendAttribute;
}

export interface Variant {
  id: number;
  sku: string;
  price: number;
  stock: number;
  attributes: VariantAttribute[];
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
  id: number;
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

// This is the type for what the backend's checkout endpoint expects.
export type CartItemForCheckout = {
    ProductVariantId: number;
    quantity: number;
};

// This is the type for the frontend's cart state.
// It holds more information for display purposes.
export type CartItem = {
  id: number; // This will be the ProductVariantId
  name: string;
  price: number;
  quantity: number;
  image: string;
  size: string;
  sku: string;
  stock: number;
};