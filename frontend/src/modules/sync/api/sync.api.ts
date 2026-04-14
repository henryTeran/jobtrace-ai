import { apiClient } from "../../../shared/api/client";

import type { SyncRequest, SyncResponse } from "../types/sync.types";

export async function runSync(payload: SyncRequest): Promise<SyncResponse> {
  const response = await apiClient.post<SyncResponse>("/emails/sync", payload, {
    timeout: 180000,
  });
  return response.data;
}
