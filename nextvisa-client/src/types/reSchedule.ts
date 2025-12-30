export const ScheduleStatus = {
    PENDING: 'PENDING',
    PROCESSING: 'PROCESSING',
    COMPLETED: 'COMPLETED',
    FAILED: 'FAILED',
    NOT_FOUND: 'NOT_FOUND',
    LOGIN_PENDING: 'LOGIN_PENDING'
} as const;

export type ScheduleStatus = typeof ScheduleStatus[keyof typeof ScheduleStatus];

export interface ReSchedule {
    id: number;
    applicant: number;
    start_datetime?: string;
    end_datetime?: string;
    status: ScheduleStatus;
    error?: string;
    created_at: string;
    updated_at: string;
}

export interface ReScheduleCreate {
    applicant: number;
    start_datetime?: string;
    end_datetime?: string;
    status?: ScheduleStatus;
    error?: string;
}

export interface ReScheduleUpdate {
    applicant?: number;
    start_datetime?: string;
    end_datetime?: string;
    status?: ScheduleStatus;
    error?: string;
}
