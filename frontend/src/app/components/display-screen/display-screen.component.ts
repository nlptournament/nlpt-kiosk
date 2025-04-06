import { Component, OnInit } from '@angular/core';
import { KioskService } from '../../services/kiosk.service';
import { Kiosk } from '../../interfaces/kiosk';
import { CommonModule } from '@angular/common';
import { Timeline } from '../../interfaces/timeline';
import { Subscription, timer } from 'rxjs';
import { TimelineService } from '../../services/timeline.service';

@Component({
  selector: 'app-display-screen',
  imports: [CommonModule],
  templateUrl: './display-screen.component.html',
  styleUrl: './display-screen.component.scss'
})
export class DisplayScreenComponent implements OnInit {
    kiosk!: Kiosk;
    timeline?: Timeline;

    refreshKioskTimer = timer(1000, 1000);
    refreshKioskTimerSubscription: Subscription | undefined;

    showMissingName: boolean = false;

    constructor(
        private kioskService: KioskService,
        private timelineService: TimelineService
    ) { }

    ngOnInit(): void {
        let myName = window.location.search.split('name=').pop()?.split('&')[0];
        if (myName)
            this.kioskService
                .getMyId(myName)
                .subscribe((id: string) => {
                    this.kioskService
                        .getKiosk(id)
                        .subscribe((kiosk: Kiosk) => {
                            this.kiosk = kiosk;
                            this.refreshTimeline();
                            this.refreshKioskTimerSubscription = this.refreshKioskTimer.subscribe(() => this.refreshKiosk());
                        });
                });
        else this.showMissingName = true;
    }

    refreshKiosk() {
        this.kioskService
            .getKiosk(this.kiosk.id)
            .subscribe((kiosk: Kiosk) => {
                if (this.kiosk.timeline_id != kiosk.timeline_id) {
                    this.kiosk = kiosk;
                    this.refreshTimeline();
                }
                else {
                    this.kiosk = kiosk;
                }
            });
    }

    refreshTimeline() {
        if (this.kiosk.timeline_id != null)
            this.timelineService
                .getTimeline(this.kiosk.timeline_id)
                .subscribe((timeline: Timeline) => {
                    this.timeline = timeline;
                });
    }
}
