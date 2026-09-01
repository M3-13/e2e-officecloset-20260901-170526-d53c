import { client } from "./client";
import type { ClothingItem, Outfit } from "./types";

export async function listItems(): Promise<ClothingItem[]> {
  return client.get<ClothingItem[]>("/wardrobe/items");
}

export async function list(): Promise<Outfit[]> {
  return client.get<Outfit[]>("/outfits");
}

export async function create(name: string, itemIds: number[]): Promise<Outfit> {
  return client.post<Outfit>("/outfits", { name, item_ids: itemIds });
}

export async function get(id: number): Promise<Outfit> {
  return client.get<Outfit>(`/outfits/${id}`);
}

export async function update(
  id: number,
  patch: { name?: string; item_ids?: number[] },
): Promise<Outfit> {
  return client.patch<Outfit>(`/outfits/${id}`, patch);
}

export async function remove(id: number): Promise<void> {
  return client.delete<void>(`/outfits/${id}`);
}
