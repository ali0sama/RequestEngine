import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AccessRequest } from '../../core/models';
import { buildWorkflowSteps, WorkflowStep } from '../../core/workflow';

@Component({
  selector: 'app-workflow-stepper',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './workflow-stepper.html',
  styleUrl: './workflow-stepper.css'
})
export class WorkflowStepper {
  @Input({ required: true }) request!: AccessRequest;

  get steps(): WorkflowStep[] {
    return buildWorkflowSteps(this.request);
  }

  icon(status: WorkflowStep['status']): string {
    const map: Record<string, string> = {
      completed: 'fa-solid fa-check',
      current: 'fa-solid fa-circle-dot',
      upcoming: 'fa-regular fa-circle',
      rejected: 'fa-solid fa-xmark',
      'info-paused': 'fa-solid fa-pause',
      'not-reached': 'fa-regular fa-circle',
    };
    return map[status] ?? 'fa-regular fa-circle';
  }
}
