import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User } from '../interfaces/user';

@Injectable({
  providedIn: 'root'
})
export class UserService {

    private userUrl = environment.apiUrl + '/user/'

    constructor(
        private http: HttpClient
    ) { }

    public getUser(id: string): Observable<User> {
        return this.http.get<User>(this.userUrl + id + '/', {withCredentials:true});
    }

    public getUsers(): Observable<User[]> {
        return this.http.get<User[]>(this.userUrl, {withCredentials:true});
    }

    public getMe(): Observable<User> {
        return this.http.get<User>(this.userUrl + 'me/', {withCredentials:true});
    }

    public updatePw(id: string, pw: string): Observable<any> {
        let user = {
            'pw': pw
        }
        return this.http.patch<any>(this.userUrl + id + '/', user, {withCredentials:true});
    }
}
