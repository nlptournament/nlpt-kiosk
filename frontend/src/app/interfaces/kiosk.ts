export interface Kiosk {
    id: string;
    name: string;
    desc?: string;
    added_by_id?: string | null;
    common?: boolean;
    timeline_id: string | null;
}

export interface KioskTlSelection {
    kiosk_id: string;
    next?: string;
    preset: string[];
}
