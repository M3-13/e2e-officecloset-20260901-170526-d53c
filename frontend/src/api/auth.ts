import { client } from "./client";
import type { AuthResponse, User } from "./types";

export function register(email: string, password: string): Promise<AuthResponse> {
  return client.post<AuthResponse>("/auth/register", { email, password });
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return client.post<AuthResponse>("/auth/login", { email, password });
}

export function me(): Promise<User> {
  return client.get<User>("/auth/me");
}
