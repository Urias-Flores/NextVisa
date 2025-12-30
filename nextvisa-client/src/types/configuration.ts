export interface Configuration {
    id: number;
    base_url: string;
    hub_address: string;
    sleep_time: number;
    push_token: string;
    push_user: string;
    df_msg: string;
    created_at: string;
    updated_at?: string;
}

export interface ConfigurationUpdate {
    base_url: string;
    hub_address: string;
    sleep_time: number;
    push_token: string;
    push_user: string;
    df_msg: string;
}
