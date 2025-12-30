import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { configurationApi } from '../services/configuration';
import type { ConfigurationUpdate } from '../types/configuration';

export const configurationKeys = {
    all: ['configuration'] as const,
    detail: () => [...configurationKeys.all, 'detail'] as const,
};

export function useConfiguration() {
    return useQuery({
        queryKey: configurationKeys.detail(),
        queryFn: () => configurationApi.get(),
    });
}

export function useUpdateConfiguration() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ id, data }: { id: number; data: ConfigurationUpdate }) =>
            configurationApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: configurationKeys.all });
        },
    });
}
