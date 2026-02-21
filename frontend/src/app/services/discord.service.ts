import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { DiscordGuild, DiscordRole } from '../interfaces/discord';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DiscordService {
    private discordguildUrl = environment.apiUrl + '/discordguild/'
    private discordroleUrl = environment.apiUrl + '/discordrole/'

    constructor(
        private http: HttpClient
    ) { }

    public getDiscordGuilds(): Observable<DiscordGuild[]> {
        return this.http.get<DiscordGuild[]>(this.discordguildUrl, {withCredentials:true});
    }

    public getDiscordRoles(): Observable<DiscordRole[]> {
        return this.http.get<DiscordRole[]>(this.discordroleUrl, {withCredentials:true});
    }
}
