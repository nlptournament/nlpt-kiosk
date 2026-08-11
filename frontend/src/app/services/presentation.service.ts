import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PresentationService {
    private presentationUrl = environment.apiUrl + '/presentation/'

    constructor(
        private http: HttpClient
    ) { }

    public execRestart(): Observable<any> {
        return this.http.put<any>(this.presentationUrl + 'restart/', {}, {withCredentials:true});
    }

    public execForward(): Observable<any> {
        return this.http.put<any>(this.presentationUrl + 'forward/', {}, {withCredentials:true});
    }

    public execBackward(): Observable<any> {
        return this.http.put<any>(this.presentationUrl + 'backward/', {}, {withCredentials:true});
    }
}
