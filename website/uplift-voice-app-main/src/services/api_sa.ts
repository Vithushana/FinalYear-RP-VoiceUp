import axios from "axios";

export const api_sa = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 20000,
});
