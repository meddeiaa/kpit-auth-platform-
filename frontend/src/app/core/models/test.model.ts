/**
 * Modèles TypeScript pour la gestion des tests.
 */

// Un Test Case Robot Framework
export interface TestCase {
  id: string;
  name: string;
  documentation: string;
  tags: string[];
  steps_count: number;
  file_name: string;
  
  // Propriétés ajoutées côté frontend
  selected?: boolean;
  lastStatus?: 'PASS' | 'FAIL' | null;
}

// Une Suite (fichier .robot)
export interface TestSuite {
  file_name: string;
  file_path: string;
  test_cases_count: number;
}

// Réponse GET /api/tests/suites
export interface SuitesResponse {
  success: boolean;
  count: number;
  suites: TestSuite[];
}

// Réponse GET /api/tests/cases
export interface TestCasesResponse {
  success: boolean;
  count: number;
  available_tags: string[];
  test_cases: TestCase[];
}

// Requête POST /api/tests/run
export interface RunTestsRequest {
  test_names?: string[];
  suite_file?: string;
  include_tags?: string[];
  exclude_tags?: string[];
}

// Résultat d'un test individuel
export interface TestResult {
  name: string;
  status: 'PASS' | 'FAIL';
}

// Réponse POST /api/tests/run
export interface RunTestsResponse {
  success: boolean;
  total: number;
  passed: number;
  failed: number;
  return_code: number;
  tests: TestResult[];
  output?: string;
  report_available: boolean;
  error?: string;
}
// Réponse de POST /run/async
export interface AsyncRunResponse {
  success: boolean;
  job_id: string;
  message: string;
}

// Log d'un test
export interface TestLog {
  timestamp: string;
  message: string;
}

// Test individuel
export interface JobTest {
  name: string;
  status: 'PASS' | 'FAIL';
}

// État d'un job
export interface JobStatus {
  id: string;
  status: 'starting' | 'running' | 'completed' | 'failed';
  started_at: string;
  ended_at: string | null;
  total: number;
  completed: number;
  passed: number;
  failed: number;
  current_test: string | null;
  tests: JobTest[];
  logs: TestLog[];
  error: string | null;
  report_available: boolean;
}

// Réponse de GET /run/status/{job_id}
export interface JobStatusResponse {
  success: boolean;
  job: JobStatus;
}

export interface TestCaseRequest {
  name: string;
  documentation?: string;
  tags?: string[];
}

export interface TestCaseMutationResponse {
  success: boolean;
  message?: string;
  error?: string;
  test?: TestCase;
}