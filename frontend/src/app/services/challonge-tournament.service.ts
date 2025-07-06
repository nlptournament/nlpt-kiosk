import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChallongeTournament } from '../interfaces/challonge-tournament';

@Injectable({
  providedIn: 'root'
})
export class ChallongeTournamentService {
    private tournamentUrl = environment.apiUrl + '/challongetournament/'

    constructor(
        private http: HttpClient
    ) { }

    public getTournament(id: string): Observable<ChallongeTournament> {
        return this.http.get<ChallongeTournament>(this.tournamentUrl + id + '/', {withCredentials:true});
    }

    public getTournaments(): Observable<ChallongeTournament[]> {
        return this.http.get<ChallongeTournament[]>(this.tournamentUrl, {withCredentials:true});
    }
}
