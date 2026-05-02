export interface Project {
  id: string;
  name: string;
  description?: string;
  base_url?: string;
  created_at: string;
  updated_at: string;
  test_count: number;
  last_run_at?: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  base_url?: string;
}

export interface AssertionConfig {
  type: string;
  name?: string;
  expected?: any;
  path?: string;
  key?: string;
  script?: string;
  schema?: object;
}

export interface TestStepConfig {
  name: string;
  method: string;
  endpoint: string;
  params?: Record<string, any>;
  headers?: Record<string, any>;
  json?: Record<string, any>;
  data?: any;
  assertions?: AssertionConfig[];
  extract?: Record<string, any>;
}

export interface TestCase {
  id: string;
  name: string;
  description?: string;
  variables?: Record<string, any>;
  steps: TestStepConfig[];
  project_id?: string;
  file_path?: string;
  created_at: string;
  updated_at: string;
  last_result?: any;
}

export interface TestCaseCreate {
  name: string;
  description?: string;
  variables?: Record<string, any>;
  steps: TestStepConfig[];
  project_id?: string;
}

export interface Environment {
  id: string;
  name: string;
  description?: string;
  base_url: string;
  variables?: Record<string, any>;
  headers?: Record<string, any>;
  project_id?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReportSummary {
  id: string;
  test_name: string;
  status: string;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  pass_rate: number;
  total_time: number;
  executed_at: string;
  report_format: string;
}

export interface TestReport extends ReportSummary {
  test_results: any[];
  error_messages?: Record<string, any>;
  environment?: string;
}

export interface ExecutionRecord {
  execution_id: string;
  test_id: string;
  status: string;
  start_time?: string;
  end_time?: string;
  result?: any;
  logs: string[];
  progress: number;
  total_steps: number;
  current_step: number;
  error?: string;
}

export interface WebSocketMessage {
  type: string;
  execution_id?: string;
  progress?: number;
  current_step?: number;
  total_steps?: number;
  result?: any;
  message?: string;
  level?: string;
  status?: string;
  error?: string;
}
