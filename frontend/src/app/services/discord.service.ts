import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { DiscordGuild, DiscordRole, DiscordChannel, DiscordPoll } from '../interfaces/discord';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DiscordService {
    private discordguildUrl = environment.apiUrl + '/discordguild/'
    private discordroleUrl = environment.apiUrl + '/discordrole/'
    private discordchannelUrl = environment.apiUrl + '/discordchannel/'
    private discordpollUrl = environment.apiUrl + '/discordpoll/'

    constructor(
        private http: HttpClient
    ) { }

    public getDiscordGuilds(): Observable<DiscordGuild[]> {
        return this.http.get<DiscordGuild[]>(this.discordguildUrl, {withCredentials:true});
    }

    public getDiscordRoles(): Observable<DiscordRole[]> {
        return this.http.get<DiscordRole[]>(this.discordroleUrl, {withCredentials:true});
    }

    public getDiscordChannels(): Observable<DiscordChannel[]> {
        return this.http.get<DiscordChannel[]>(this.discordchannelUrl, {withCredentials:true});
    }

    public getDiscordPolls(): Observable<DiscordPoll[]> {
        return this.http.get<DiscordPoll[]>(this.discordpollUrl, {withCredentials:true});
    }

    public getFilteredDiscordPolls(channel_ids: string[] = [], guild_id: string = '', only_active: boolean = true): Observable<DiscordPoll[]> {
        let body = {
            'only_active': only_active,
            'guild_id': guild_id,
            'channel_ids': channel_ids
        }
        return this.http.post<DiscordPoll[]>(this.discordpollUrl + 'filter/', body, {withCredentials:true});
    }
}
