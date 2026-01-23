const isProduction = import.meta.env.PROD;

export const API_BASE_URL = isProduction ? "/api" : `http://${window.location.hostname}:8000`;
