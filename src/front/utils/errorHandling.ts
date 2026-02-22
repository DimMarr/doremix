import { AlertManager } from "@utils/alertManager";

export function handleHttpError(response: Response, context: string) {
  switch (response.status) {
    case 401:
      new AlertManager().error("Authentication required.");
      break;
    case 403:
      new AlertManager().error("You are not allowed to do this action.");
      break;
    case 429:
      new AlertManager().warning("Too many requests. Please slow down.");
      break;
    case 404:
      new AlertManager().error(`${context} not found.`);
      break;
    case 500:
    case 502:
    case 503:
      new AlertManager().error("Server error. Please try again later.");
      break;
    default:
      new AlertManager().error(`Failed to ${context.toLowerCase()}.`);
  }
}
