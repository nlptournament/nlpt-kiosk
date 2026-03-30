import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GameAbbr } from '../interfaces/game-abbr';

@Injectable({
  providedIn: 'root'
})
export class GameAbbrService {
  private abbrUrl = environment.apiUrl + '/gameabbr/'

  constructor(
      private http: HttpClient
  ) { }

  public getGameAbbr(id: string): Observable<GameAbbr> {
      return this.http.get<GameAbbr>(this.abbrUrl + id + '/', {withCredentials:true});
  }

  public getGameAbbrs(): Observable<GameAbbr[]> {
      return this.http.get<GameAbbr[]>(this.abbrUrl, {withCredentials:true});
  }

  public updateGameAbbr(abbr: GameAbbr): Observable<any> {
      return this.http.patch<any>(this.abbrUrl + abbr.id + '/', abbr, {withCredentials:true});
  }

  public createGameAbbr(abbr: GameAbbr): Observable<any> {
      return this.http.post<any>(this.abbrUrl, abbr, {withCredentials:true});
  }

  public deleteGameAbbr(id: string): Observable<any> {
      return this.http.delete<any>(this.abbrUrl + id + '/', {withCredentials:true});
  }
}
