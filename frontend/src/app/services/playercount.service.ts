import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Playercount, PlayercountDiscord } from '../interfaces/playercount';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PlayercountService {
    private playercountUrl = environment.apiUrl + '/playercounts/'

    constructor(
        private http: HttpClient
    ) { }

    public getPlayercounts(): Observable<Playercount[]> {
        return this.http.get<Playercount[]>(this.playercountUrl, {withCredentials:true});
    }

    public getPlayercountsDiscord(): Observable<PlayercountDiscord[]> {
        return this.http.get<PlayercountDiscord[]>(this.playercountUrl + 'discord/', {withCredentials:true});
    }
}
