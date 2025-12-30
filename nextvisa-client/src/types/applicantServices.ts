import type { ScheduleStatus } from "./reSchedule";

export interface Applicant {
    id: number;
    name: string;
    last_name: string;
    email: string;
    schedule_date?: string;
    min_date?: string;
    max_date?: string;
    schedule?: string;
    re_schedule_status?: ScheduleStatus;
    created_at: string;
    updated_at: string;
}

export interface ApplicantCreate {
    name: string;
    last_name: string;
    email: string;
    password: string;
    schedule_date?: string;
    min_date?: string;
    max_date?: string;
    schedule?: string;
}

export interface ApplicantUpdate {
    name?: string;
    last_name?: string;
    email?: string;
    password?: string;
    schedule_date?: string;
    min_date?: string;
    max_date?: string;
    schedule?: string;
}