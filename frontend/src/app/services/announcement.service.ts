import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Announcement } from '../interfaces/announcement';

@Injectable({
  providedIn: 'root'
})
export class AnnouncementService {
    private announcementUrl = environment.apiUrl + '/announcements/'

    constructor(
        private http: HttpClient
    ) { }

    public getAnnouncements(): Observable<Announcement[]> {
        return this.http.get<Announcement[]>(this.announcementUrl, {withCredentials:true});
    }
}
