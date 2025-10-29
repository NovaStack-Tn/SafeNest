// User & Auth Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  organization: number;
  role: string;
  department?: string;
  avatar?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// Dashboard Types
export interface DashboardStats {
  time_range: string;
  logins: {
    total: number;
    successful: number;
    failed: number;
    anomalies: number;
  };
  alerts: {
    total: number;
    open: number;
    critical: number;
  };
  incidents: {
    total: number;
    open: number;
    critical: number;
  };
  faces: {
    detections: number;
    matches: number;
  };
}

// Alert Types
export interface Alert {
  id: number;
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'acknowledged' | 'resolved';
  alert_type: string;
  created_at: string;
  acknowledged_at?: string;
}

// Incident Types
export interface IncidentCategory {
  id: number;
  organization: number;
  name: string;
  description: string;
  color: string;
  icon: string;
  severity_default: 'low' | 'medium' | 'high' | 'critical';
  is_active: boolean;
  created_at: string;
  incident_count: number;
}

export interface Incident {
  id: number;
  title: string;
  description: string;
  incident_type: string;
  category?: number;
  category_name?: string;
  category_color?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'contained' | 'resolved' | 'closed';
  assignee?: number;
  assignee_name?: string;
  created_by?: number;
  created_by_name?: string;
  organization: number;
  opened_at: string;
  closed_at?: string;
  updated_at: string;
  event_count: number;
  evidence_count: number;
  tags: string[];
  metadata: Record<string, any>;
  ai_generated: boolean;
  ai_confidence?: number;
  extracted_entities?: Record<string, any>;
  has_resolution: boolean;
  events?: IncidentEvent[];
  evidence?: Evidence[];
  resolution?: IncidentResolution;
}

export interface IncidentEvent {
  id: number;
  incident: number;
  action: string;
  description: string;
  actor?: number;
  actor_name?: string;
  metadata: Record<string, any>;
  timestamp: string;
}

export interface Evidence {
  id: number;
  incident: number;
  file: string;
  file_name: string;
  file_url?: string;
  file_size: number;
  file_hash: string;
  kind: 'frame' | 'image' | 'log' | 'document' | 'other';
  description: string;
  uploaded_by?: number;
  uploaded_by_name?: string;
  uploaded_at: string;
  metadata: Record<string, any>;
}

export interface IncidentResolution {
  id: number;
  incident: number;
  resolution_type: 'resolved' | 'false_positive' | 'duplicate' | 'mitigated' | 'escalated' | 'cannot_fix';
  summary: string;
  actions_taken: string;
  root_cause: string;
  preventive_measures: string;
  related_incidents: number[];
  resolved_by?: number;
  resolved_by_name?: string;
  resolved_at: string;
  time_to_detect?: string;
  time_to_resolve?: string;
  metadata: Record<string, any>;
}

// Face Recognition Types
export interface FaceIdentity {
  id: number;
  person_label: string;
  person_meta: Record<string, any>;
  photo?: string;
  is_active: boolean;
  enrollment_status: 'pending' | 'enrolled' | 'failed';
  embedding_count: number;
  detection_count: number;
}

export interface FaceDetection {
  id: number;
  camera_name: string;
  identity_label?: string;
  is_match: boolean;
  similarity?: number;
  confidence: number;
  timestamp: string;
  frame_url?: string;
}

export interface Camera {
  id: number;
  name: string;
  location: string;
  active: boolean;
  last_detection_at?: string;
}

// LLM/Chat Types
export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ChatSession {
  id: number;
  bot_type: 'assistant' | 'recommendation' | 'analysis';
  title: string;
  created_at: string;
  message_count: number;
}

// Login Event Types
export interface LoginEvent {
  id: number;
  username: string;
  ip_address: string;
  country_name?: string;
  success: boolean;
  is_anomaly: boolean;
  timestamp: string;
}
