import client from './client';
import type { ExecutionRecord } from '../types';

export const executionApi = {
  run: (testId: string, envId?: string) =>
    client.post(`/api/execution/${testId}/run`, null, { params: { env_id: envId } }).then(r => r.data),
  runBatch: (testIds: string[], envId?: string) =>
    client.post('/api/execution/batch/run', testIds, { params: { env_id: envId } }).then(r => r.data),
  getStatus: (executionId: string) =>
    client.get<ExecutionRecord>(`/api/execution/${executionId}/status`).then(r => r.data),
  getHistory: () => client.get<ExecutionRecord[]>('/api/execution/history').then(r => r.data),
  stop: (executionId: string) => client.post(`/api/execution/${executionId}/stop`).then(r => r.data),
};
