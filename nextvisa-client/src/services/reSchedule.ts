import apiClient from './api';
import type { ReSchedule, ReScheduleCreate, ReScheduleUpdate } from '../types/reSchedule';

export const reScheduleApi = {
    getAll: async (limit?: number, offset?: number): Promise<ReSchedule[]> => {
        const params = new URLSearchParams();
        if (limit) params.append('limit', limit.toString());
        if (offset) params.append('offset', offset.toString());

        const response = await apiClient.get<ReSchedule[]>(`/re-schedules?${params}`);
        return response.data;
    },

    getById: async (id: number): Promise<ReSchedule> => {
        const response = await apiClient.get<ReSchedule>(`/re-schedules/${id}`);
        return response.data;
    },

    getByApplicant: async (applicantId: number, limit?: number): Promise<ReSchedule[]> => {
        const params = new URLSearchParams();
        if (limit) params.append('limit', limit.toString());

        const response = await apiClient.get<ReSchedule[]>(`/re-schedules/applicant/${applicantId}?${params}`);
        return response.data;
    },

    create: async (data: ReScheduleCreate): Promise<ReSchedule> => {
        const response = await apiClient.post<ReSchedule>('/re-schedules', data);
        return response.data;
    },

    update: async (id: number, data: ReScheduleUpdate): Promise<ReSchedule> => {
        const response = await apiClient.put<ReSchedule>(`/re-schedules/${id}`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await apiClient.delete(`/re-schedules/${id}`);
    }
};
