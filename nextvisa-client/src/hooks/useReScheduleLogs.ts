import { useQuery } from '@tanstack/react-query';
import { getReScheduleLogsByReScheduleId } from '../services/api/reScheduleLogs';
import type { ReScheduleLog } from '../types/reScheduleLog';

export const useReScheduleLogs = (reScheduleId: number) => {
    return useQuery<ReScheduleLog[], Error>({
        queryKey: ['reScheduleLogs', reScheduleId],
        queryFn: () => getReScheduleLogsByReScheduleId(reScheduleId),
        enabled: !!reScheduleId,
    });
};
