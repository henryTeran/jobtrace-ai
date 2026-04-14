export type SyncRequest = {
  providers: Array<"gmail" | "outlook">;
  limit_per_provider: number;
  mode: "strict" | "full";
  from_date?: string;
  to_date?: string;
};

export type SyncResponse = {
  fetched: number;
  filtered: number;
  inserted: number;
  duplicates: number;
};
