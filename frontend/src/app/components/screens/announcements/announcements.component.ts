import { CommonModule } from '@angular/common';
import { Component, input, OnDestroy, OnInit } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { Announcement } from '../../../interfaces/announcement';
import { AnnouncementService } from '../../../services/announcement.service';
import { MediaService } from '../../../services/media.service';

@Component({
  selector: 'screen-announcements',
  imports: [CommonModule],
  templateUrl: './announcements.component.html',
  styleUrl: './announcements.component.scss'
})
export class AnnouncementsComponent implements OnInit, OnDestroy {
    isActive = input.required<boolean>();

    refreshTimesTimer = timer(1000, 1000);
    refreshTimesTimerSubscription: Subscription | undefined;
    refreshAnnouncementsTimer = timer(10000, 10000);
    refreshAnnouncementsTimerSubscription: Subscription | undefined;

    announcements: Announcement[] =[];

    constructor(
        private announcementService: AnnouncementService,
        private mediaService: MediaService
    ) {}

    ngOnInit(): void {
        this.refreshAnnouncements();
        this.refreshTimesTimerSubscription = this.refreshTimesTimer.subscribe(() => this.updateDisplays());
        this.refreshAnnouncementsTimerSubscription = this.refreshAnnouncementsTimer.subscribe(() => this.refreshAnnouncements());
    }

    ngOnDestroy(): void {
        this.refreshTimesTimerSubscription?.unsubscribe();
        this.refreshAnnouncementsTimerSubscription?.unsubscribe();
    }

    refreshAnnouncements() {
        this.announcementService
            .getAnnouncements().subscribe({
                next: (announce: Announcement[]) => {
                    this.updateDisplays(announce);
                },
                error: () => {}
            });
    }

    updateDisplays(announce: Announcement[] | undefined = undefined) {
        for (let anno of (announce ? announce : this.announcements)) {
            if (anno.target) {
                let diff: number = anno.target - Date.now() / 1000;
                if (Math.floor(diff) <= 0) anno.display_time = 'jetzt';
                else {
                    let h: number = Math.floor(diff / 3600);
                    diff = diff % 3600;
                    let m: number = Math.floor(diff / 60);
                    let s: number = Math.floor(diff % 60);
                    anno.display_time = (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
                }
            } else anno.display_time = null;
            if (anno.img) {
                anno.img_url = this.mediaService.getMediaUrl(undefined, anno.img);
            } else  anno.img_url = null;
        }
        if (announce) this.announcements = announce;
    }
}
