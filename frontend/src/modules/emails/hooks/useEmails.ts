import { useQuery } from "@tanstack/react-query";

import { mapAxiosError } from "../../../shared/api/errors";
import { getEmails } from "../api/emails.api";
import type { GetEmailsParams } from "../types/emails.types";

export function useEmails(params: GetEmailsParams) {
  const query = useQuery({
    queryKey: ["emails", params],
    queryFn: () => getEmails(params),
    placeholderData: (previousData) => previousData,
  });

  return {
    ...query,
    mappedError: query.error ? mapAxiosError(query.error) : null,
  };
}
