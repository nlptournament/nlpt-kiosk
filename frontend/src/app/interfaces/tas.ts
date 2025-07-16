export interface TasChallengeRank {
    rank: number;
    player: string;
    time?: number | null;
    active: boolean;
}

export interface TasGlobalRank {
    rank: number;
    player: string;
    points: number;
    active: boolean;
}
