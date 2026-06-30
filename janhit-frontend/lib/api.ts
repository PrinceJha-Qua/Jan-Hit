// Thin client for the JanHit FastAPI backend.
// Base URL comes from env so it works in dev (localhost:8000) and prod.
import type { Beneficiary } from './demo-data';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API ${path} failed: ${res.status} ${body}`);
  }
  return res.json();
}

// Backend response shapes (snake_case, matches Pydantic schemas).
export interface ApiEligibilityResult {
  id: string;
  scheme_id: string;
  scheme_name: string;
  department: string;
  benefit_amount: string;
  status: 'eligible' | 'pending' | 'needs-documents';
  why_eligible: string;
  missing_documents: string[];
  next_step: string;
}

export interface ApiActionStep {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'in-progress' | 'pending' | 'blocked';
  owner: string;
  due_date: string | null;
}

export interface ApiCase {
  id: string;
  beneficiary_id: string;
  status: 'pending' | 'in-progress' | 'completed' | 'needs-follow-up';
  created_at: string;
  updated_at: string;
}

export interface ApiAssessment {
  id: string;
  case_id: string;
  beneficiary_id: string;
  created_at: string;
}

// Step 1: submit the assessment form -> creates beneficiary + case + assessment.
export function createAssessment(beneficiary: Beneficiary) {
  return request<ApiAssessment>('/assessments', {
    method: 'POST',
    body: JSON.stringify({
      beneficiary: {
        name: beneficiary.name,
        age: beneficiary.age,
        district: beneficiary.district,
        occupation: beneficiary.occupation,
        annual_income: beneficiary.annualIncome,
        is_widow: beneficiary.isWidow,
        is_farmer: beneficiary.isFarmer,
        has_disability: beneficiary.hasDisability,
        caste: beneficiary.caste,
        gender: beneficiary.gender,
      },
    }),
  });
}

// Step 2: run the deterministic rule engine for that assessment.
export function runEligibility(assessmentId: string) {
  return request<ApiEligibilityResult[]>(`/assessments/${assessmentId}/eligibility`, {
    method: 'POST',
  });
}

// Step 3: generate the action plan timeline for the case.
export function generateActionPlan(caseId: string) {
  return request<ApiActionStep[]>(`/cases/${caseId}/action-plan`, {
    method: 'POST',
  });
}

export function getActionPlan(caseId: string) {
  return request<ApiActionStep[]>(`/cases/${caseId}/action-plan`);
}

// Step 4: create a public shareable token for the Citizen Record screen.
export function createShareLink(caseId: string) {
  return request<{ token: string; url_path: string }>(`/cases/${caseId}/share`, {
    method: 'POST',
  });
}

export function getCitizenRecord(token: string) {
  return request<{
    beneficiary: any;
    eligible_count: number;
    schemes: ApiEligibilityResult[];
    next_step: ApiActionStep | null;
  }>(`/citizen-record/${token}`);
}

// Workspace screen: list cases, optionally filtered by status.
export function listCases(status?: string) {
  const qs = status && status !== 'all' ? `?status=${encodeURIComponent(status)}` : '';
  return request<ApiCase[]>(`/cases${qs}`);
}

export function updateCaseStatus(caseId: string, status: string) {
  return request<ApiCase>(`/cases/${caseId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

// District Intelligence screen.
export function getDistrictStats() {
  return request<{
    total_cases: number;
    pending_cases: number;
    completed_this_month: number;
    schemes_disbursed: number;
    top_schemes: { name: string; count: number }[];
    monthly_trend: { month: string; cases: number }[];
  }>('/analytics/district');
}
