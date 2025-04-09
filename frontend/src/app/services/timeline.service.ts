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

    public updateTimeline(timeline: Timeline): Observable<any> {
        return this.http.patch<any>(this.timelineUrl + timeline.id + '/', timeline, {withCredentials:true});
    }

    public createTimeline(timeline: Timeline): Observable<any> {
        return this.http.post<any>(this.timelineUrl, timeline, {withCredentials:true});
    }

    public deleteTimeline(id: string): Observable<any> {
        return this.http.delete<any>(this.timelineUrl + id + '/', {withCredentials:true});
    }

    public setCurrentPos(timeline: Timeline): Observable<number> {
        let data = {
            'kiosk_id': timeline.kiosk_id,
            'current_pos': timeline.current_pos
        };
        return this.http.put<number>(this.timelineUrl + 'currentPos/' + timeline.id + '/', data);
    }
}
