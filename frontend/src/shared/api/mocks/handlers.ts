import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("http://127.0.0.1:8000/health", () => HttpResponse.json({ status: "ok" })),
  http.get("http://127.0.0.1:8000/auth/status", () =>
    HttpResponse.json({
      providers: [
        { provider: "gmail", connected: false, updated_at: null },
        { provider: "outlook", connected: false, updated_at: null },
      ],
    }),
  ),
];
