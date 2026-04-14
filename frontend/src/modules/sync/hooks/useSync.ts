import { useMutation, useQueryClient } from "@tanstack/react-query";

import { mapAxiosError } from "../../../shared/api/errors";
import { runSync } from "../api/sync.api";

export function useSync() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: runSync,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["emails"] }),
        queryClient.invalidateQueries({ queryKey: ["dashboard", "summary"] }),
      ]);
    },
  });

  return {
    ...mutation,
    mappedError: mutation.error ? mapAxiosError(mutation.error) : null,
  };
}
