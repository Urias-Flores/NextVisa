import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reScheduleApi } from '../services/reSchedule';
import type { ReScheduleCreate, ReScheduleUpdate } from '../types/reSchedule';

// Query keys
export const reScheduleKeys = {
    all: ['reSchedules'] as const,
    lists: () => [...reScheduleKeys.all, 'list'] as const,
    list: (filters?: { limit?: number; offset?: number }) =>
        [...reScheduleKeys.lists(), { filters }] as const,
    byApplicant: (applicantId: number) => [...reScheduleKeys.all, 'applicant', applicantId] as const,
    details: () => [...reScheduleKeys.all, 'detail'] as const,
    detail: (id: number) => [...reScheduleKeys.details(), id] as const,
};

// Fetch all re-schedules
export const useReSchedules = (limit?: number, offset?: number) => {
    return useQuery({
        queryKey: reScheduleKeys.list({ limit, offset }),
        queryFn: () => reScheduleApi.getAll(limit, offset),
        staleTime: 1000 * 60 * 1, // 1 minute
    });
};

// Fetch re-schedules by applicant
export const useReSchedulesByApplicant = (applicantId: number, limit?: number) => {
    return useQuery({
        queryKey: reScheduleKeys.byApplicant(applicantId),
        queryFn: () => reScheduleApi.getByApplicant(applicantId, limit),
        enabled: !!applicantId,
    });
};

// Fetch single re-schedule by ID
export const useReSchedule = (id: number) => {
    return useQuery({
        queryKey: reScheduleKeys.detail(id),
        queryFn: () => reScheduleApi.getById(id),
        enabled: !!id && id > 0,
    });
};

// Create re-schedule mutation
export const useCreateReSchedule = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: ReScheduleCreate) => reScheduleApi.create(data),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: reScheduleKeys.lists() });
            queryClient.invalidateQueries({ queryKey: reScheduleKeys.byApplicant(variables.applicant) });
        },
    });
};

// Update re-schedule mutation
export const useUpdateReSchedule = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: ReScheduleUpdate }) =>
            reScheduleApi.update(id, data),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: reScheduleKeys.detail(data.id) });
            queryClient.invalidateQueries({ queryKey: reScheduleKeys.lists() });
            queryClient.invalidateQueries({ queryKey: reScheduleKeys.byApplicant(data.applicant) });
        },
    });
};

// Delete re-schedule mutation
export const useDeleteReSchedule = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => reScheduleApi.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: reScheduleKeys.lists() });
            // Note: We might want to invalidate applicant specific queries too, 
            // but we don't have the applicant ID here easily without returning it from delete
            queryClient.invalidateQueries({ queryKey: reScheduleKeys.all });
        },
    });
};
