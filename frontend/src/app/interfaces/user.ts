export interface User {
    id?: string;
    admin: boolean;
    streamer: boolean;
    login: string;
    pw?: string | null;
    hidden_elements: string[];
}
