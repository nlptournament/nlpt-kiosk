export interface User {
    id?: string;
    admin: boolean;
    streamer: boolean;
    prefer_single_shot: boolean;
    login: string;
    pw?: string | null;
    hidden_elements: string[];
}
