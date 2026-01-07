export const LogState = {
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    SUCCESS: 'SUCCESS'
} as const;

export type LogState = typeof LogState[keyof typeof LogState];

export interface ReScheduleLog {
    id: number;
    re_schedule: number;
    state: LogState;
    content: string;
    created_at: string;
}
