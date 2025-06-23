import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User } from '../interfaces/user';
import { Md5 } from 'ts-md5';
import * as CryptoJS from 'crypto-js';

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

    public updateUser(user: User): Observable<any> {
        return this.http.patch<any>(this.userUrl + user.id + '/', user, {withCredentials:true});
    }

    public createUser(user: User): Observable<any> {
        return this.http.post<any>(this.userUrl, user, {withCredentials:true});
    }

    public deleteUser(id: string): Observable<any> {
        return this.http.delete<any>(this.userUrl + id + '/', {withCredentials:true});
    }

    public getMe(): Observable<User> {
        return this.http.get<User>(this.userUrl + 'me/', {withCredentials:true});
    }

    public addHide(user_id: string, element_id: string): Observable<any> {
        return this.http.put<any>(this.userUrl + user_id + '/hide_add/', {'element_id': element_id}, {withCredentials:true});
    }

    public delHide(user_id: string, element_id: string): Observable<any> {
        return this.http.put<any>(this.userUrl + user_id + '/hide_del/', {'element_id': element_id}, {withCredentials:true});
    }

    public updatePw(id: string, old_pw: string, new_pw: string): Observable<any> {
        let key = CryptoJS.MD5(old_pw);
        let iv = CryptoJS.lib.WordArray.random(16);
        var cipher = CryptoJS.AES.encrypt(new_pw, key, {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
            });

        let result = {
            'iv': iv.toString(),
            'pw': cipher.ciphertext.toString(),
            'cs': CryptoJS.MD5(key.toString() + iv.toString() + cipher.ciphertext.toString()).toString()
        }

        return this.http.put<any>(this.userUrl + '/password/' + id + '/', result, {withCredentials:true});
    }
}
