export interface Screen {
    id: string;
    desc?: string;
    template_id?: string;
    user_id?: string;
    duration: number | null;
    repeat: number;
    loop: boolean;
    variables: any;
    locked?: boolean;
    key: string;
}
