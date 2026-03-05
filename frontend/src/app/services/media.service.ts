import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Media } from '../interfaces/media';

@Injectable({
  providedIn: 'root'
})
export class MediaService {
    private mediaUrl = environment.apiUrl + '/media/'

    constructor(
        private http: HttpClient
    ) { }

    public getMedia(id: string): Observable<Media> {
        return this.http.get<Media>(this.mediaUrl + id + '/', {withCredentials:true});
    }

    public getMedias(): Observable<Media[]> {
        return this.http.get<Media[]>(this.mediaUrl, {withCredentials:true});
    }

    public updateMedia(media: Media): Observable<any> {
        return this.http.patch<any>(this.mediaUrl + media.id + '/', media, {withCredentials:true});
    }

    public createMedia(media: Media): Observable<any> {
        return this.http.post<any>(this.mediaUrl, media, {withCredentials:true});
    }

    public deleteMedia(id: string): Observable<any> {
        return this.http.delete<any>(this.mediaUrl + id + '/', {withCredentials:true});
    }

    public uploadMediaFile(id: string, file: File): Observable<any> {
        const formData = new FormData();
        formData.append('upload', file);
        return this.http.post<any>(this.mediaUrl + id + '/s3/', formData, {withCredentials:true});
    }

    public getMediaUrl(media: Media | undefined = undefined, s3_id: string | undefined = undefined, preview: boolean = false): string {
        if (media) {
            if (media.src_type == 1) {
                if (preview) return this.mediaUrl + media.id + '/s3/';
                else return environment.s3MediaUrl + '/' + media.id;
            }
            else {
                return media.src;
            }
        }
        if (s3_id) {
            if (preview) return this.mediaUrl + s3_id + '/s3/';
            else return environment.s3MediaUrl + '/' + s3_id;
        }
        return '';
    }
}
