export interface Timeline {
    id: string | null;
    template_id?: string | null;
    kiosk_id?: string;
    screen_ids: string[];
    start_pos: number;
    current_pos: number;
    start_time: number | null;
    single_shot: boolean;
    locked?: boolean;
    displayed?: boolean;
    default?: boolean;
    preset?: boolean;
}
