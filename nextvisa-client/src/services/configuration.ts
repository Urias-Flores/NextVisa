import { apiClient } from './api';
import type { Configuration, ConfigurationUpdate } from '../types/configuration';

export const configurationApi = {
    get: async (): Promise<Configuration> => {
        const response = await apiClient.get<Configuration>('/configuration');
        return response.data;
    },

    update: async (id: number, data: ConfigurationUpdate): Promise<Configuration> => {
        const response = await apiClient.put<Configuration>(`/configuration/${id}`, data);
        return response.data;
    }
};
