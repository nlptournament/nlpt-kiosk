import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChallongeParticipant } from '../interfaces/challonge-participant';

@Injectable({
  providedIn: 'root'
})
export class ChallongeParticipantService {
    private participantUrl = environment.apiUrl + '/challongeparticipant/'

    constructor(
        private http: HttpClient
    ) { }

    public getParticipant(id: string): Observable<ChallongeParticipant> {
        return this.http.get<ChallongeParticipant>(this.participantUrl + id + '/', {withCredentials:true});
    }

    public getParticipants(): Observable<ChallongeParticipant[]> {
        return this.http.get<ChallongeParticipant[]>(this.participantUrl, {withCredentials:true});
    }
}
