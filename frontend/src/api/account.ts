import { client } from "./client";

export function removeAccount(): Promise<void> {
  return client.delete<void>("/account/me");
}
