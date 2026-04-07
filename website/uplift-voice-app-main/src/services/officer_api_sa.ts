import axios from "axios";
import type { ComplaintListItem, OfficerOutput } from "../components/types_sa/complaint_types_sa";

const api = axios.create({
  baseURL: "http://127.0.0.1:5004/api",
});

export async function getAllComplaints(): Promise<ComplaintListItem[]> {
  const res = await api.get("/complaints/all");
  return res.data;
}

export async function getComplaintById(id: number): Promise<OfficerOutput> {
  const res = await api.get(`/officer/complaint/${id}`);
  return res.data;
}

// `last_update` helper removed — backend no longer exposes lightweight summary.
