export interface ChallongeTournament {
    id: string;
    name: string;
    url: string;
    state: number;
    type: string;
    game: string;
    available_rounds: number[];
    completed_rounds: number[];
}
