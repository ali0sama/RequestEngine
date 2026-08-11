import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkflowStepper } from './workflow-stepper';
import { AccessRequest, WorkflowHistory } from '../../core/models';

function makeHistory(overrides: Partial<WorkflowHistory>): WorkflowHistory {
  return {
    id: 1,
    from_state: 'DRAFT',
    to_state: 'PENDING_MANAGER',
    action: 'SUBMIT',
    actor: 1,
    actor_username: 'requester1',
    comment: '',
    timestamp: '',
    ...overrides,
  };
}

function makeRequest(overrides: Partial<AccessRequest>): AccessRequest {
  return {
    id: 1,
    requester: 1,
    requester_username: 'requester1',
    application: 1,
    application_name: 'Jira',
    justification: 'Need access',
    current_state: 'DRAFT',
    current_owner: null,
    current_owner_username: null,
    returned_from_state: null,
    created_at: '',
    updated_at: '',
    history: [],
    ...overrides,
  };
}

describe('WorkflowStepper', () => {
  let component: WorkflowStepper;
  let fixture: ComponentFixture<WorkflowStepper>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WorkflowStepper],
    }).compileComponents();

    fixture = TestBed.createComponent(WorkflowStepper);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.request = makeRequest({});
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('marks the current draft as the current step and the rest upcoming', () => {
    component.request = makeRequest({ current_state: 'DRAFT' });
    fixture.detectChanges();
    const steps = component.steps;
    expect(steps.find((s) => s.state === 'DRAFT')?.status).toBe('current');
    expect(steps.find((s) => s.state === 'PENDING_MANAGER')?.status).toBe('upcoming');
  });

  it('marks every step completed once approved', () => {
    component.request = makeRequest({ current_state: 'APPROVED' });
    fixture.detectChanges();
    expect(component.steps.every((s) => s.status === 'completed')).toBe(true);
  });

  it('marks the rejecting stage and stops the path afterward when rejected', () => {
    component.request = makeRequest({
      current_state: 'REJECTED',
      history: [
        makeHistory({ id: 1, from_state: 'DRAFT', to_state: 'PENDING_MANAGER', action: 'SUBMIT' }),
        makeHistory({ id: 2, from_state: 'PENDING_MANAGER', to_state: 'REJECTED', action: 'REJECT' }),
      ],
    });
    fixture.detectChanges();
    const steps = component.steps;
    expect(steps.find((s) => s.state === 'DRAFT')?.status).toBe('completed');
    expect(steps.find((s) => s.state === 'PENDING_MANAGER')?.status).toBe('rejected');
    expect(steps.find((s) => s.state === 'PENDING_APP_OWNER')?.status).toBe('not-reached');
  });

  it('marks the resume stage as info-paused when info requested', () => {
    component.request = makeRequest({
      current_state: 'INFO_REQUESTED',
      returned_from_state: 'PENDING_APP_OWNER',
      history: [
        makeHistory({ id: 1, from_state: 'DRAFT', to_state: 'PENDING_MANAGER', action: 'SUBMIT' }),
        makeHistory({ id: 2, from_state: 'PENDING_MANAGER', to_state: 'PENDING_APP_OWNER', action: 'APPROVE' }),
        makeHistory({ id: 3, from_state: 'PENDING_APP_OWNER', to_state: 'INFO_REQUESTED', action: 'RETURN' }),
      ],
    });
    fixture.detectChanges();
    const steps = component.steps;
    expect(steps.find((s) => s.state === 'PENDING_APP_OWNER')?.status).toBe('info-paused');
    expect(steps.find((s) => s.state === 'PENDING_SECURITY')?.status).toBe('upcoming');
  });

  it('marks the manager step as completed (not crossed-out) when it was skipped for having no manager', () => {
    component.request = makeRequest({
      current_state: 'PENDING_APP_OWNER',
      history: [
        makeHistory({ id: 1, from_state: 'DRAFT', to_state: 'PENDING_APP_OWNER', action: 'SUBMIT' }),
      ],
    });
    fixture.detectChanges();
    const steps = component.steps;
    expect(steps.find((s) => s.state === 'PENDING_MANAGER')?.status).toBe('completed');
    expect(steps.find((s) => s.state === 'PENDING_APP_OWNER')?.status).toBe('current');
  });
});
