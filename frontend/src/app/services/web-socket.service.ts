import { Injectable } from '@angular/core';
import { WebSocketSubject, webSocket } from 'rxjs/webSocket';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
    private socket$: WebSocketSubject<any>;

    constructor() {
        this.socket$ = webSocket(environment.wssUrl);
    }

    sendMessage(message: any) {
        this.socket$.next(message);
    }

    getKioskMessages(): Observable<any> {
        return this.socket$.asObservable();
    }

    getAdminMessages(): Observable<any> {
        let cookie: string = this.getCookie('NLPT-Kiosk-Controller');
        if (cookie.length > 0) this.sendMessage({'session': cookie});
        return this.socket$.asObservable();
    }

    closeConnection() {
        this.socket$.complete();
    }

    private getCookie(name: string) {
        let ca: Array<string> = document.cookie.split(';');
        let caLen: number = ca.length;
        let cookieName = `${name}=`;
        let c: string;

        for (let i: number = 0; i < caLen; i += 1) {
            c = ca[i].replace(/^\s+/g, '');
            if (c.indexOf(cookieName) == 0) {
                return c.substring(cookieName.length, c.length);
            }
        }
        return '';
    }
}
