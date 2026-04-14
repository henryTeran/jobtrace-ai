import { AxiosError } from "axios";

import type { ApiError } from "../types/api";

type BackendErrorPayload = {
  detail?: string;
};

export function mapAxiosError(error: unknown): ApiError {
  if (!(error instanceof AxiosError)) {
    return {
      code: "UNKNOWN_ERROR",
      message: "Une erreur inattendue est survenue.",
    };
  }

  if (!error.response) {
    if (error.code === "ECONNABORTED") {
      return {
        code: "TIMEOUT_ERROR",
        message: "La requete a depasse le delai. La synchronisation peut etre encore en cours sur le backend.",
      };
    }

    return {
      code: "NETWORK_ERROR",
      message: "Impossible de joindre le serveur.",
    };
  }

  const status = error.response.status;
  const payload = error.response.data as BackendErrorPayload | undefined;

  if (status === 401) {
    return { code: "UNAUTHORIZED", message: "Session invalide ou expirée.", status };
  }
  if (status === 403) {
    return { code: "FORBIDDEN", message: "Accès refusé.", status };
  }
  if (status === 404) {
    return { code: "NOT_FOUND", message: "Ressource introuvable.", status };
  }
  if (status === 422) {
    return {
      code: "VALIDATION_ERROR",
      message: payload?.detail ?? "Données invalides.",
      status,
      details: error.response.data,
    };
  }
  if (status >= 500) {
    return { code: "SERVER_ERROR", message: "Erreur serveur temporaire.", status };
  }

  return {
    code: "UNKNOWN_ERROR",
    message: payload?.detail ?? "Une erreur est survenue.",
    status,
    details: error.response.data,
  };
}
