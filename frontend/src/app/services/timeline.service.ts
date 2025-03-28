import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Timeline } from '../interfaces/timeline';

@Injectable({
  providedIn: 'root'
})
export class TimelineService {
    private timelineUrl = environment.apiUrl + '/timeline/'

    constructor(
        private http: HttpClient
    ) { }

    public getTimeline(id: string): Observable<Timeline> {
        return this.http.get<Timeline>(this.timelineUrl + id + '/', {withCredentials:true});
    }

    public getTimelines(): Observable<Timeline[]> {
        return this.http.get<Timeline[]>(this.timelineUrl, {withCredentials:true});
    }

    public updateTimeline(kiosk: Timeline): Observable<any> {
        return this.http.patch<any>(this.timelineUrl + kiosk.id + '/', kiosk, {withCredentials:true});
    }

    public createTimeline(kiosk: Timeline): Observable<any> {
        return this.http.post<any>(this.timelineUrl, kiosk, {withCredentials:true});
    }

    public deleteTimeline(id: string): Observable<any> {
        return this.http.delete<any>(this.timelineUrl + id + '/', {withCredentials:true});
    }
}
