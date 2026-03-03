import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Kiosk } from '../interfaces/kiosk';

@Injectable({
  providedIn: 'root'
})
export class KioskService {
    private kioskUrl = environment.apiUrl + '/kiosk/'

    constructor(
        private http: HttpClient
    ) { }

    public getKiosk(id: string): Observable<Kiosk> {
        return this.http.get<Kiosk>(this.kioskUrl + id + '/', {withCredentials:true});
    }

    public getKiosks(): Observable<Kiosk[]> {
        return this.http.get<Kiosk[]>(this.kioskUrl, {withCredentials:true});
    }

    public getMyId(name: string): Observable<string> {
        return this.http.put<string>(this.kioskUrl + 'my_id/' + name + '/', {});
    }

    public updateKiosk(kiosk: Kiosk): Observable<any> {
        return this.http.patch<any>(this.kioskUrl + kiosk.id + '/', kiosk, {withCredentials:true});
    }

    public createKiosk(kiosk: Kiosk): Observable<any> {
        return this.http.post<any>(this.kioskUrl, kiosk, {withCredentials:true});
    }

    public deleteKiosk(id: string): Observable<any> {
        return this.http.delete<any>(this.kioskUrl + id + '/', {withCredentials:true});
    }

    public syncedApply(data: any): Observable<any> {
        return this.http.put<string>(this.kioskUrl + 'synced_apply/', data, {withCredentials:true});
    }

    public syncedApplyDefault(kiosk_ids: string[]): Observable<any> {
        return this.http.put<string>(this.kioskUrl + 'synced_apply_default/', kiosk_ids, {withCredentials:true});
    }

    public applyDefault(id: string): Observable<boolean> {
        return this.http.put<boolean>(this.kioskUrl + 'apply_default/' + id + '/', {}, {withCredentials:true});
    }

    public applyTimelineTemplate(kiosk_id: string, template_id: string): Observable<boolean> {
        return this.http.put<boolean>(this.kioskUrl + 'apply_timelinetemplate/' + kiosk_id + '/', {'template_id': template_id}, {withCredentials:true});
    }
}
