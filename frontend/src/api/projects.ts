import client from './client';
import type { Project, ProjectCreate } from '../types';

export const projectApi = {
  list: () => client.get<Project[]>('/api/projects').then(r => r.data),
  get: (id: string) => client.get<Project>(`/api/projects/${id}`).then(r => r.data),
  create: (data: ProjectCreate) => client.post<Project>('/api/projects', data).then(r => r.data),
  update: (id: string, data: Partial<ProjectCreate>) => client.put<Project>(`/api/projects/${id}`, data).then(r => r.data),
  delete: (id: string) => client.delete(`/api/projects/${id}`),
  getStats: (id: string) => client.get(`/api/projects/${id}/stats`).then(r => r.data),
};
