import client from './client';
import type { ReportSummary, TestReport } from '../types';

export const reportApi = {
  list: (testId?: string, limit = 50) => {
    const params: any = { limit };
    if (testId) params.test_id = testId;
    return client.get<ReportSummary[]>('/api/reports', { params }).then(r => r.data);
  },
  get: (id: string) => client.get<TestReport>(`/api/reports/${id}`).then(r => r.data),
  delete: (id: string) => client.delete(`/api/reports/${id}`),
  export: (id: string, format = 'json') =>
    client.get(`/api/reports/${id}/export`, { params: { format } }).then(r => r.data),
  getStats: () => client.get('/api/reports/stats').then(r => r.data),
};
