import { AccessRequest } from './models';

export const LINEAR_STATES = [
  'DRAFT',
  'PENDING_MANAGER',
  'PENDING_APP_OWNER',
  'PENDING_SECURITY',
  'APPROVED',
];

export const STATE_LABELS: Record<string, string> = {
  DRAFT: 'Draft',
  PENDING_MANAGER: 'Pending Manager',
  PENDING_APP_OWNER: 'Pending App Owner',
  PENDING_SECURITY: 'Pending Security',
  INFO_REQUESTED: 'Info Requested',
  APPROVED: 'Approved',
  REJECTED: 'Rejected',
};

export const STATE_CLASSES: Record<string, string> = {
  DRAFT: 'badge-draft',
  PENDING_MANAGER: 'badge-pending',
  PENDING_APP_OWNER: 'badge-pending',
  PENDING_SECURITY: 'badge-pending',
  INFO_REQUESTED: 'badge-info',
  APPROVED: 'badge-approved',
  REJECTED: 'badge-rejected',
};

export function statusLabel(state: string): string {
  return STATE_LABELS[state] ?? state;
}

export function statusClass(state: string): string {
  return STATE_CLASSES[state] ?? 'badge-draft';
}

export type StepStatus =
  | 'completed'
  | 'current'
  | 'upcoming'
  | 'rejected'
  | 'info-paused'
  | 'not-reached';

export interface WorkflowStep {
  state: string;
  label: string;
  status: StepStatus;
}

/**
 * Builds the full 5-stage happy-path stepper (Draft -> Manager -> App Owner ->
 * Security -> Approved) with each step's status derived from the request's
 * current_state, returned_from_state, and history — covering the REJECTED,
 * INFO_REQUESTED, and no-manager-skip branches that current_state alone can't
 * express.
 */
export function buildWorkflowSteps(req: AccessRequest): WorkflowStep[] {
  const steps: WorkflowStep[] = LINEAR_STATES.map((state) => ({
    state,
    label: STATE_LABELS[state],
    status: 'upcoming' as StepStatus,
  }));

  const managerSkipped = req.history.some(
    (h) => h.action === 'SUBMIT' && h.to_state === 'PENDING_APP_OWNER'
  );
  if (managerSkipped) {
    const idx = steps.findIndex((s) => s.state === 'PENDING_MANAGER');
    if (idx !== -1) steps[idx].status = 'completed';
  }

  if (req.current_state === 'REJECTED') {
    const rejectEntry = [...req.history].reverse().find((h) => h.action === 'REJECT');
    const rejectedAtIndex = rejectEntry ? LINEAR_STATES.indexOf(rejectEntry.from_state) : -1;

    steps.forEach((step, i) => {
      if (rejectedAtIndex === -1) return;
      if (i < rejectedAtIndex) step.status = 'completed';
      else if (i === rejectedAtIndex) step.status = 'rejected';
      else step.status = 'not-reached';
    });
    return steps;
  }

  if (req.current_state === 'INFO_REQUESTED') {
    const resumeIndex = req.returned_from_state ? LINEAR_STATES.indexOf(req.returned_from_state) : -1;

    steps.forEach((step, i) => {
      if (resumeIndex === -1) return;
      if (i < resumeIndex) step.status = 'completed';
      else if (i === resumeIndex) step.status = 'info-paused';
      else step.status = 'upcoming';
    });
    return steps;
  }

  const currentIndex = LINEAR_STATES.indexOf(req.current_state);
  steps.forEach((step, i) => {
    if (currentIndex === -1) return;
    if (req.current_state === 'APPROVED') step.status = 'completed';
    else if (i < currentIndex) step.status = 'completed';
    else if (i === currentIndex) step.status = 'current';
    else step.status = 'upcoming';
  });

  return steps;
}
