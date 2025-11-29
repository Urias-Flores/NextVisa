import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { applicantApi } from '../services/applicant';
import type { ApplicantCreate, ApplicantUpdate } from '../types/applicantServices';

// Query keys
export const applicantKeys = {
    all: ['applicants'] as const,
    lists: () => [...applicantKeys.all, 'list'] as const,
    list: (filters?: { limit?: number; offset?: number }) =>
        [...applicantKeys.lists(), { filters }] as const,
    details: () => [...applicantKeys.all, 'detail'] as const,
    detail: (id: number) => [...applicantKeys.details(), id] as const,
};

// Fetch all applicants
export const useApplicants = (limit?: number, offset?: number) => {
    return useQuery({
        queryKey: applicantKeys.list({ limit, offset }),
        queryFn: () => applicantApi.getAll(limit, offset),
        staleTime: 1000 * 60 * 5, // 5 minutes
        retry: 2,
    });
};

// Fetch single applicant
export const useApplicant = (id: number) => {
    return useQuery({
        queryKey: applicantKeys.detail(id),
        queryFn: () => applicantApi.getById(id),
        enabled: !!id,
        staleTime: 1000 * 60 * 5,
    });
};

// Create applicant mutation
export const useCreateApplicant = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (applicant: ApplicantCreate) => applicantApi.create(applicant),
        onSuccess: () => {
            // Invalidate and refetch applicants list
            queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
        },
    });
};

// Update applicant mutation
export const useUpdateApplicant = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: ApplicantUpdate }) =>
            applicantApi.update(id, data),
        onSuccess: (_, variables) => {
            // Invalidate specific applicant and list
            queryClient.invalidateQueries({ queryKey: applicantKeys.detail(variables.id) });
            queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
        },
    });
};

// Delete applicant mutation
export const useDeleteApplicant = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => applicantApi.delete(id),
        onSuccess: () => {
            // Invalidate applicants list
            queryClient.invalidateQueries({ queryKey: applicantKeys.lists() });
        },
    });
};

// Test credentials mutation
export const useTestCredentials = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => applicantApi.testCredentials(id),
        onSuccess: (data, id) => {
            // Invalidate applicant query to refresh data
            queryClient.invalidateQueries({ queryKey: applicantKeys.detail(id) });
        },
    });
};
