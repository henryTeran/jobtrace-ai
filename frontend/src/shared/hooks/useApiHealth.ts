import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../api/client";

export function useApiHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const response = await apiClient.get<{ status: string }>("/health");
      return response.data;
    },
  });
}
