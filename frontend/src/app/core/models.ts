export interface Application {
  id: number;
  name: string;
  owner: number;
  owner_username: string;
  description: string;
}

export interface WorkflowHistory {
  id: number;
  from_state: string;
  to_state: string;
  action: string;
  actor: number;
  actor_username: string;
  comment: string;
  timestamp: string;
}

export interface AccessRequest {
  id: number;
  requester: number;
  requester_username: string;
  application: number;
  application_name: string;
  justification: string;
  current_state: string;
  current_owner: number | null;
  current_owner_username: string | null;
  returned_from_state: string | null;
  created_at: string;
  updated_at: string;
  history: WorkflowHistory[];
}

export interface WorkflowAction {
  comment?: string;
}
