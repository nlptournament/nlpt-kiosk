import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ScreenTemplate } from '../interfaces/screen-template';

@Injectable({
  providedIn: 'root'
})
export class ScreenTemplateService {
    private stUrl = environment.apiUrl + '/screentemplate/'

    constructor(
        private http: HttpClient
    ) { }

    public getScreenTemplate(id: string): Observable<ScreenTemplate> {
        return this.http.get<ScreenTemplate>(this.stUrl + id + '/', {withCredentials:true});
    }

    public getScreenTemplates(): Observable<ScreenTemplate[]> {
        return this.http.get<ScreenTemplate[]>(this.stUrl, {withCredentials:true});
    }
}
