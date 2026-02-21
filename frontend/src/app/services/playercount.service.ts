import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient, HttpParams } from '@angular/common/http';
import { PlayercountPrometheus, PlayercountDiscord } from '../interfaces/playercount';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PlayercountService {
    private playercountUrl = environment.apiUrl + '/playercounts/'

    constructor(
        private http: HttpClient
    ) { }

    public getPlayercountsPrometheus(): Observable<PlayercountPrometheus[]> {
        return this.http.get<PlayercountPrometheus[]>(this.playercountUrl, {withCredentials:true});
    }

    public getPlayercountsDiscord(guild_id: string | undefined, role_id: string | undefined): Observable<PlayercountDiscord[]> {
        let req_params = new HttpParams();
        if (guild_id) req_params = req_params.set('guild', guild_id);
        if (role_id) req_params = req_params.set('role', role_id);
        return this.http.get<PlayercountDiscord[]>(this.playercountUrl + 'discord/', {withCredentials:true, params: req_params});
    }
}
