import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AccessRequest, Application, WorkflowHistory } from './models';

@Injectable({ providedIn: 'root' })
export class RequestService {

  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // ── Requests ─────────────────────────────────────────────────────────────

  getMyRequests(): Observable<AccessRequest[]> {
    return this.http.get<AccessRequest[]>(`${this.api}/requests/`);
  }

  getRequest(id: number): Observable<AccessRequest> {
    return this.http.get<AccessRequest>(`${this.api}/requests/${id}/`);
  }

  createRequest(applicationId: number, justification: string): Observable<AccessRequest> {
    return this.http.post<AccessRequest>(`${this.api}/requests/`, {
      application: applicationId,
      justification
    });
  }

  // ── Workflow actions ──────────────────────────────────────────────────────

  submitRequest(id: number, comment = ''): Observable<AccessRequest> {
    return this.http.post<AccessRequest>(`${this.api}/requests/${id}/submit/`, { comment });
  }

  approveRequest(id: number, comment = ''): Observable<AccessRequest> {
    return this.http.post<AccessRequest>(`${this.api}/requests/${id}/approve/`, { comment });
  }

  rejectRequest(id: number, comment = ''): Observable<AccessRequest> {
    return this.http.post<AccessRequest>(`${this.api}/requests/${id}/reject/`, { comment });
  }

  returnForInfo(id: number, comment = ''): Observable<AccessRequest> {
    return this.http.post<AccessRequest>(`${this.api}/requests/${id}/return_for_info/`, { comment });
  }

  resubmitRequest(id: number, comment = ''): Observable<AccessRequest> {
    return this.http.post<AccessRequest>(`${this.api}/requests/${id}/resubmit/`, { comment });
  }

  // ── Approver views ────────────────────────────────────────────────────────

  getPendingApprovals(): Observable<AccessRequest[]> {
    return this.http.get<AccessRequest[]>(`${this.api}/requests/pending_approvals/`);
  }

  getNeedsMyResponse(): Observable<AccessRequest[]> {
    return this.http.get<AccessRequest[]>(`${this.api}/requests/needs_my_response/`);
  }

  // ── History ───────────────────────────────────────────────────────────────

  getHistory(id: number): Observable<WorkflowHistory[]> {
    return this.http.get<WorkflowHistory[]>(`${this.api}/requests/${id}/history/`);
  }

  // ── Applications ──────────────────────────────────────────────────────────

  getApplications(): Observable<Application[]> {
    return this.http.get<Application[]>(`${this.api}/applications/`);
  }
}
