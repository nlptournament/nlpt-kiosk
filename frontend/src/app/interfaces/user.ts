export interface User {
    id?: string;
    admin: boolean;
    login: string;
    pw?: string | null;
    hidden_elements: string[];
}
