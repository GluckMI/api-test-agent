import client from './client';
import type { TestCase, TestCaseCreate } from '../types';

export const testApi = {
  list: (projectId?: string) => {
    const params = projectId ? { project_id: projectId } : {};
    return client.get<TestCase[]>('/api/tests', { params }).then(r => r.data);
  },
  get: (id: string) => client.get<TestCase>(`/api/tests/${id}`).then(r => r.data),
  create: (data: TestCaseCreate) => client.post<TestCase>('/api/tests', data).then(r => r.data),
  update: (id: string, data: Partial<TestCaseCreate>) => client.put<TestCase>(`/api/tests/${id}`, data).then(r => r.data),
  delete: (id: string) => client.delete(`/api/tests/${id}`),
  getYaml: (id: string) => client.get<{ yaml_content: string }>(`/api/tests/${id}/yaml`).then(r => r.data),
  createFromYaml: (yamlContent: string, projectId?: string) =>
    client.post<TestCase>('/api/tests/from-yaml', { yaml_content: yamlContent, project_id: projectId }).then(r => r.data),
};
