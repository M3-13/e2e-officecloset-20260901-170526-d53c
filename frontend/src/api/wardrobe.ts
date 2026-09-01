import { client } from "./client";
import type { Category, ClothingItem } from "./types";

export interface CreateItemInput {
  name: string;
  category: Category;
  color?: string;
  brand?: string;
  image?: File;
}

export interface UpdateItemInput {
  name?: string;
  category?: Category;
  color?: string;
  brand?: string;
  image?: File;
}

function toFormData(input: CreateItemInput | UpdateItemInput): FormData {
  const form = new FormData();
  if (input.name !== undefined) form.append("name", input.name);
  if (input.category !== undefined) form.append("category", input.category);
  if (input.color !== undefined) form.append("color", input.color);
  if (input.brand !== undefined) form.append("brand", input.brand);
  if (input.image !== undefined) form.append("image", input.image);
  return form;
}

export function listItems(category?: Category): Promise<ClothingItem[]> {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return client.get<ClothingItem[]>(`/wardrobe/items${query}`);
}

export function createItem(input: CreateItemInput): Promise<ClothingItem> {
  return client.post<ClothingItem>("/wardrobe/items", toFormData(input));
}

export function updateItem(id: number, input: UpdateItemInput): Promise<ClothingItem> {
  return client.patch<ClothingItem>(`/wardrobe/items/${id}`, toFormData(input));
}

export function removeItem(id: number): Promise<void> {
  return client.delete<void>(`/wardrobe/items/${id}`);
}
