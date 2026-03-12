export interface Screen {
    id?: string | null;
    desc: string;
    template_id?: string;
    user_id?: string;
    header: string;
    duration: number | null;
    till: number | null;
    repeat: number;
    loop: boolean;
    variables: any;
    locked?: boolean;
    displayed?: boolean;
    default?: boolean;
    key: string;
}
