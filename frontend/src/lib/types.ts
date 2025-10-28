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
export interface Incident {
  id: number;
  title: string;
  description: string;
  incident_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'contained' | 'resolved' | 'closed';
  assignee?: number;
  assignee_name?: string;
  created_by_name?: string;
  opened_at: string;
  closed_at?: string;
  event_count: number;
  evidence_count: number;
}

export interface IncidentEvent {
  id: number;
  action: string;
  description: string;
  actor_name?: string;
  timestamp: string;
}

export interface Evidence {
  id: number;
  file_name: string;
  file_url?: string;
  kind: string;
  uploaded_by_name?: string;
  uploaded_at: string;
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
