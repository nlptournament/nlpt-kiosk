export interface Kiosk {
    id: string;
    name: string;
    desc?: string;
    added_by_id?: string | null;
    common?: boolean;
    timeline_id: string | null;
}
