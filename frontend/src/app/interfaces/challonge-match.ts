export interface ChallongeMatch {
    id: string;
    tournament_id: string;
    state: number;
    round: number;
    player1_id: string | null;
    player2_id: string | null;
    winner_id: string | null;
}
