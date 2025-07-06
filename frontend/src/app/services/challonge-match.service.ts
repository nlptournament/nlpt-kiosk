import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { ChallongeMatch } from '../interfaces/challonge-match';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChallongeMatchService {
    private matchUrl = environment.apiUrl + '/challongematch/'

    constructor(
        private http: HttpClient
    ) { }

    public getMatch(id: string): Observable<ChallongeMatch> {
        return this.http.get<ChallongeMatch>(this.matchUrl + id + '/', {withCredentials:true});
    }

    public getMatches(): Observable<ChallongeMatch[]> {
        return this.http.get<ChallongeMatch[]>(this.matchUrl, {withCredentials:true});
    }
}
