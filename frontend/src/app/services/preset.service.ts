import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Preset } from '../interfaces/preset';

@Injectable({
  providedIn: 'root'
})
export class PresetService {
    private presetUrl = environment.apiUrl + '/preset/'

    constructor(
        private http: HttpClient
    ) { }

    public getPreset(id: string): Observable<Preset> {
        return this.http.get<Preset>(this.presetUrl + id + '/', {withCredentials:true});
    }

    public getPresets(): Observable<Preset[]> {
        return this.http.get<Preset[]>(this.presetUrl, {withCredentials:true});
    }

    public updatePreset(preset: Preset): Observable<any> {
        return this.http.patch<any>(this.presetUrl + preset.id + '/', preset, {withCredentials:true});
    }

    public createPreset(preset: Preset): Observable<any> {
        return this.http.post<any>(this.presetUrl, preset, {withCredentials:true});
    }

    public deletePreset(id: string): Observable<any> {
        return this.http.delete<any>(this.presetUrl + id + '/', {withCredentials:true});
    }

    public applyPreset(id: string): Observable<any> {
        return this.http.put<any>(this.presetUrl + 'apply/' + id + '/', {}, {withCredentials:true});
    }
}
