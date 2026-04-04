export type OfficerOutput_sa = {
  summary: {
    complaint_id: number;
    category: string;
    priority_level: number;
    priority_label: string;
    priority_score: number;
    risk_category: string;
    recommended_action_time: string;
  };

  complaint: {
    expanded_text: string;
  };

  location: {
    latitude: number;
    longitude: number;
    location_link?: string | null;
  };

  why_this_priority: string[];

  gis: {
    gis_score: number;
    gis_summary: string;
    details_for_popup?: Record<string, any>;
  };

  recurring: {
    recurring_count: number;
    is_recurring: boolean;
    recurring_reason: string;
  };

  ai_suggestion: {
    priority_level_ml?: number | null;
    confidence?: number | null;
    note?: string | null;
  };

  track: {
    track: string;
    reason: string;
  };
};
