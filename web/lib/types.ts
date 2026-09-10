export type Layer = {
  id: string;
  label: string;
  path: string;
  kind: "rgb" | "score" | "agreement";
};

export type CaseStudy = {
  case: {
    case_id: string;
    title: string;
    aoi_name: string;
    bbox: [number, number, number, number];
    baseline_period: string;
    comparison_period: string;
    analysis_crs: string;
    analysis_resolution_m: number;
    data_mode: string;
    evidence_status: string;
  };
  status: {
    label: string;
    evidence_status: string;
    claims_locked: boolean;
    synthetic_fixture: boolean;
    message: string;
  };
  question: string;
  methods: { id: string; name: string; role: string }[];
  metrics: {
    candidate_area_ha: number;
    candidate_pixels: number;
    agreement_fraction: number;
    embedding_distance_p95: number;
    minimum_valid_pixel_fraction: number;
  };
  time_series: { date: string; ndvi: number; ndbi: number }[];
  quality: { date: string; valid_fraction: number }[];
  layers: Layer[];
  candidates: {
    id: string;
    label: string;
    area_ha: number;
    score: number;
    interpretation: string;
  }[];
  limitations: string[];
  learning: { start_here: string; next_exercise: string };
};
