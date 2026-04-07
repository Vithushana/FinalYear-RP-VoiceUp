export type ComplaintListItem = {
  id: number;
  category: "road" | "garbage";
  text_expanded: string;
  latitude: number;
  longitude: number;
  location_link?: string | null;
  created_at?: string;
  priority_level?: number;
  priority_score?: number;
};

// 1. GIS Spatial Data-vukkana puthu Interfaces
export interface GISDetail {
  name: string;
  type: string;
  distance: number;
  priority?: number;
  distance_m?: number;
}

export interface GISData {
  gis_score: number;
  gis_summary: string;
  junction_density?: number;
  nearby_complaint_count?: number;
  alternate_routes_count?: number;
  nearest_alt_crossing_km?: number;
  nearest_alt_point_lat?: number | null;
  nearest_alt_point_lon?: number | null;
  nearest_alt_point_name?: string | null;
  officer_display_summary?: string;
  details_for_popup: {
    poi_score: number;
    road_score: number;
    connectivity_score: number;
    crowd_score?: number;
    complaint_density_score?: number;
  };
  poi_details: GISDetail[];
}

// 2. Main Officer Output Interface
export type OfficerOutput = {
  summary: {
    complaint_id: number;
    category: string;
    priority_level: number;
    priority_label: string;
    priority_score: number;
    risk_category: string;
    recommended_action_time: string;
  };
  complaint: { expanded_text: string };
  location: { latitude: number; 
              longitude: number; 
              location_link: string | null
              place_hint?: string | null };
  why_this_priority: string[];
  // GISData-vukku ippo link panniyachu
  gis: GISData; 
  recurring: any;
  track?: {
    track?: string;
    reason?: string;
    responsible_unit?: string;
    suggested_action?: string;
    why?: string[];
  };
  officer_brief?: {
    situation?: string;
    likely_impact?: string[];
    handling_note?: string;
    officer_check?: string[];
    
  };

};