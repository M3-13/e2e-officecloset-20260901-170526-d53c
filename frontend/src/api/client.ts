const API_BASE = "/api";

export class ApiError extends Error {
  status: number;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
  }
}

function getToken(): string | null {
  try {
    return localStorage.getItem("token");
  } catch {
    return null;
  }
}

export function getAuthToken(): string | null {
  return getToken();
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as unknown as T;
  }
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    const body = await response.json();
    if (!response.ok) {
      const detail =
        typeof body?.detail === "string" ? body.detail : "Unerwarteter Fehler";
      throw new ApiError(response.status, detail);
    }
    return body as T;
  }
  if (!response.ok) {
    throw new ApiError(response.status, response.statusText);
  }
  return (await response.text()) as unknown as T;
}

async function request<T>(
  method: string,
  path: string,
  options: { body?: unknown; auth?: boolean } = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  let body: BodyInit | undefined;
  if (options.body !== undefined) {
    if (options.body instanceof FormData) {
      body = options.body;
    } else {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(options.body);
    }
  }
  const response = await fetch(`${API_BASE}${path}`, { method, headers, body });
  return parseResponse<T>(response);
}

export const client = {
  get<T>(path: string): Promise<T> {
    return request<T>("GET", path);
  },
  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("POST", path, { body });
  },
  patch<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("PATCH", path, { body });
  },
  delete<T>(path: string): Promise<T> {
    return request<T>("DELETE", path);
  },
};

export function apiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unerwarteter Fehler";
}
