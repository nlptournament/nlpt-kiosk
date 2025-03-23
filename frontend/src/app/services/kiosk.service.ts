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

    public updateKiosk(kiosk: Kiosk): Observable<any> {
        return this.http.patch<any>(this.kioskUrl + kiosk.id + '/', kiosk, {withCredentials:true});
    }

    public createKiosk(kiosk: Kiosk): Observable<any> {
        return this.http.post<any>(this.kioskUrl, kiosk, {withCredentials:true});
    }

    public deleteKiosk(id: string): Observable<any> {
        return this.http.delete<any>(this.kioskUrl + id + '/', {withCredentials:true});
    }
}
