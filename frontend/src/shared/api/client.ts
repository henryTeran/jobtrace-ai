import axios from "axios";

import { env } from "../config/env";

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  config.headers.set("Content-Type", "application/json");
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error),
);
