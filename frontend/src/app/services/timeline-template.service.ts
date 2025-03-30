import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TimelineTemplate } from '../interfaces/timeline-template';

@Injectable({
  providedIn: 'root'
})
export class TimelineTemplateService {
    private ttUrl = environment.apiUrl + '/timelinetemplate/'

    constructor(
        private http: HttpClient
    ) { }

    public getTimelineTemplate(id: string): Observable<TimelineTemplate> {
        return this.http.get<TimelineTemplate>(this.ttUrl + id + '/', {withCredentials:true});
    }

    public getTimelineTemplates(): Observable<TimelineTemplate[]> {
        return this.http.get<TimelineTemplate[]>(this.ttUrl, {withCredentials:true});
    }

    public updateTimelineTemplate(tt: TimelineTemplate): Observable<any> {
        return this.http.patch<any>(this.ttUrl + tt.id + '/', tt, {withCredentials:true});
    }

    public createTimelineTemplate(tt: TimelineTemplate): Observable<any> {
        return this.http.post<any>(this.ttUrl, tt, {withCredentials:true});
    }

    public deleteTimelineTemplate(id: string): Observable<any> {
        return this.http.delete<any>(this.ttUrl + id + '/', {withCredentials:true});
    }

    public updateTimelines(id: string): Observable<any> {
        return this.http.put<any>(this.ttUrl + 'update_timelines/' + id + '/', {}, {withCredentials:true});
    }
}
