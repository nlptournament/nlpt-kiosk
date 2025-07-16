import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TasChallengeRank, TasGlobalRank } from '../interfaces/tas';

@Injectable({
  providedIn: 'root'
})
export class TasService {
    private tasUrl = environment.apiUrl + '/tas/'

    constructor(
        private http: HttpClient
    ) { }

    public getChallengeRanks(): Observable<TasChallengeRank[]> {
        return this.http.get<TasChallengeRank[]>(this.tasUrl + 'challenge_ranks/', {withCredentials:true});
    }

    public getGlobalRanks(): Observable<TasGlobalRank[]> {
        return this.http.get<TasGlobalRank[]>(this.tasUrl + 'global_ranks/', {withCredentials:true});
    }
}
