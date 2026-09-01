export type Category = "top" | "bottom" | "shoes" | "accessory";

export interface User {
  id: number;
  email: string;
}

export interface ClothingItem {
  id: number;
  name: string;
  category: Category;
  color: string | null;
  brand: string | null;
  image_url: string | null;
  created_at: string;
}

export interface Outfit {
  id: number;
  name: string;
  items: ClothingItem[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
