import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Setting } from '../interfaces/setting';

@Injectable({
  providedIn: 'root'
})
export class SettingService {
    private settingUrl = environment.apiUrl + '/setting/'

    constructor(
        private http: HttpClient
    ) { }

    public getSetting(id: string): Observable<Setting> {
        return this.http.get<Setting>(this.settingUrl + id + '/', {withCredentials:true});
    }

    public getSettings(): Observable<Setting[]> {
        return this.http.get<Setting[]>(this.settingUrl, {withCredentials:true});
    }

    public updateSetting(setting: Setting): Observable<any> {
        return this.http.patch<any>(this.settingUrl + setting.id + '/', setting, {withCredentials:true});
    }
}
