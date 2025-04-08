import { CommonModule } from '@angular/common';
import { Component, input, OnInit } from '@angular/core';
import { Subscription, timer } from 'rxjs';

interface Announcement {
    layout: string;
    title: string;
    msg: string;
    target: number;
    time: string | undefined;
    img: string | undefined;
}

@Component({
  selector: 'screen-announcements',
  imports: [CommonModule],
  templateUrl: './announcements.component.html',
  styleUrl: './announcements.component.scss'
})
export class AnnouncementsComponent implements OnInit {
    isActive = input.required<boolean>();

    refreshTimesTimer = timer(1000, 1000);
    refreshTimesTimerSubscription: Subscription | undefined;

    announce: Announcement[] =[];

    ngOnInit(): void {
        this.announce.push({layout: 'default', title: 'Test', msg: 'Eine Nachricht', target: 15, time: 'jetzt', img: ''});
        this.announce.push({layout: 'danger', title: 'Pommes fassen', msg: 'Ein Flasche Pommes bitte', target: 1426, time: '00:23:45', img: ''});
        this.announce.push({layout: 'ffa', title: 'Fall Guys', msg: 'Alle zusammen um 02:00 Uhr.', target: 5027, time: '01:23:45', img: 'FallGuys.jpg'});
        this.announce.push({layout: 'default', title: 'Heizung aus', msg: 'Eis für alle, Eis für alle. Oder geht einfach schlafen!', target: 8628, time: '02:23:45', img: ''});

        for (let anno of this.announce) anno.target = Date.now() / 1000 + anno.target;
        this.updateTimes();
        this.refreshTimesTimerSubscription = this.refreshTimesTimer.subscribe(() => this.updateTimes());
    }

    updateTimes() {
        for (let anno of this.announce) {
            let diff: number = anno.target - Date.now() / 1000;
            if (Math.floor(diff) <= 0) anno.time = 'jetzt';
            else {
                let h: number = Math.floor(diff / 3600);
                diff = diff % 3600;
                let m: number = Math.floor(diff / 60);
                let s: number = Math.floor(diff % 60);
                anno.time = (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
            }
        }
    }
}
