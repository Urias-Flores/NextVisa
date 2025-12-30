import api from './api';
import type { Applicant, ApplicantCreate, ApplicantUpdate } from '../types/applicantServices';

// Applicant API endpoints
export const applicantApi = {
    // Get all applicants
    getAll: async (limit?: number, offset?: number): Promise<Applicant[]> => {
        const params = new URLSearchParams();
        if (limit) params.append('limit', limit.toString());
        if (offset) params.append('offset', offset.toString());

        const response = await api.get<Applicant[]>(`/applicants?${params}`);
        return response.data;
    },

    // Get applicant by ID
    getById: async (id: number): Promise<Applicant> => {
        const response = await api.get<Applicant>(`/applicants/${id}`);
        return response.data;
    },

    // Create new applicant
    create: async (applicant: ApplicantCreate): Promise<Applicant> => {
        const response = await api.post<Applicant>('/applicants', applicant);
        return response.data;
    },

    // Update applicant
    update: async (id: number, applicant: ApplicantUpdate): Promise<Applicant> => {
        const response = await api.put<Applicant>(`/applicants/${id}`, applicant);
        return response.data;
    },

    // Delete applicant
    delete: async (id: number): Promise<void> => {
        await api.delete(`/applicants/${id}`);
    },

    // Test credentials
    testCredentials: async (id: number): Promise<{ success: boolean; schedule: string | null; error: string | null }> => {
        const response = await api.post(`/applicants/${id}/test-credentials`);
        return response.data;
    }
};
