export interface ScreenTemplate {
    id: string;
    key: string;
    name: string;
    desc: string;
    endless: boolean;
    duration: number | null;
    variables_def: any;
}
