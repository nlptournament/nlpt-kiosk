export interface DiscordGuild {
    id: string;
    name: string;
}

export interface DiscordRole {
    id: string;
    guild_id: string;
    name: string;
}

export interface DiscordChannel {
    id: string;
    guild_id: string;
    name: string;
}

export interface DiscordPoll {
    id: string;
    question: string;
    options: string[];
    channel_id?: string;
    active: boolean;
    till_ts: number | null;
    display_time: string | null;
}
