import client from './client';
import type { Environment } from '../types';

export const environmentApi = {
  list: (projectId?: string) => {
    const params = projectId ? { project_id: projectId } : {};
    return client.get<Environment[]>('/api/environments', { params }).then(r => r.data);
  },
  get: (id: string) => client.get<Environment>(`/api/environments/${id}`).then(r => r.data),
  create: (data: Partial<Environment>) => client.post<Environment>('/api/environments', data).then(r => r.data),
  update: (id: string, data: Partial<Environment>) => client.put<Environment>(`/api/environments/${id}`, data).then(r => r.data),
  delete: (id: string) => client.delete(`/api/environments/${id}`),
  getActive: (projectId?: string) => {
    const params = projectId ? { project_id: projectId } : {};
    return client.get<Environment>('/api/environments/active', { params }).then(r => r.data);
  },
};
