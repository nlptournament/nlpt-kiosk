import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Screen } from '../interfaces/screen';

@Injectable({
  providedIn: 'root'
})
export class ScreenService {
    private screenUrl = environment.apiUrl + '/screen/'

    constructor(
        private http: HttpClient
    ) { }

    public getScreen(id: string): Observable<Screen> {
        return this.http.get<Screen>(this.screenUrl + id + '/', {withCredentials:true});
    }

    public getScreens(): Observable<Screen[]> {
        return this.http.get<Screen[]>(this.screenUrl, {withCredentials:true});
    }
}
