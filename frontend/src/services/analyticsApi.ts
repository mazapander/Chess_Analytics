import type { Overview } from "../types/analytics";

const API_URL = import.meta.env.VITE_ANALYTICS_API_URL ?? "http://localhost:8002";

export async function getOverview(signal?: AbortSignal): Promise<Overview> {
  const response = await fetch(`${API_URL}/api/v1/analytics/overview`, { signal });
  if (!response.ok) {
    throw new Error(`No se pudo cargar el análisis (${response.status})`);
  }
  return response.json() as Promise<Overview>;
}
