// api.ts
import axios from "axios";

// Create an axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
  },
  // Add timeout
  timeout: 10000,
  // Ensure we have proper CORS behavior
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

// Add request interceptor for debugging
if (typeof window !== "undefined" && process.env.NODE_ENV === "development") {
  api.interceptors.request.use(
    (config) => {
      // Log request details
      console.log("API Request:", {
        url: config.url,
        baseURL: config.baseURL,
        method: config.method,
        headers: config.headers,
        withCredentials: config.withCredentials,
        timeout: config.timeout,
        data: config.data,
      });
    return config;
  });

  api.interceptors.response.use(
    (response) => {
      console.log("Response:", {
        status: response.status,
        data: response.data,
        headers: response.headers,
      });
      return response;
    },
    (error) => {
      console.error("API Error:", {
        config: error.config,
        code: error.code,
        name: error.name,
        message: error.message,
        response: error.response?.data,
      });
      return Promise.reject(error);
    }
  );
}

export default api;