import apiClient from '../api';
import type { ReScheduleLog } from '../../types/reScheduleLog';

export const getReScheduleLogsByReScheduleId = async (reScheduleId: number): Promise<ReScheduleLog[]> => {
    const response = await apiClient.get<ReScheduleLog[]>(`/re-schedule-logs/${reScheduleId}`);
    return response.data;
};
