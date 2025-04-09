import { Component, OnInit } from '@angular/core';
import { Subscription, timer } from 'rxjs';

import { Kiosk } from '../../interfaces/kiosk';
import { Timeline } from '../../interfaces/timeline';
import { Screen } from '../../interfaces/screen';

import { KioskService } from '../../services/kiosk.service';
import { TimelineService } from '../../services/timeline.service';
import { ScreenService } from '../../services/screen.service';

import { CommonModule } from '@angular/common';
import { AnnouncementsComponent } from '../screens/announcements/announcements.component';
import { LogoStarfieldComponent } from '../screens/logo-starfield/logo-starfield.component';
import { PlayerCountsComponent } from '../screens/player-counts/player-counts.component';
import { TasComponent } from '../screens/tas/tas.component';
import { TimerComponent } from '../screens/timer/timer.component';


interface screenDP {
    screen: Screen;
    active: boolean;
    startTS: number | null;
}

@Component({
  selector: 'app-display',
  imports: [CommonModule, AnnouncementsComponent, LogoStarfieldComponent, PlayerCountsComponent, TasComponent, TimerComponent],
  templateUrl: './display.component.html',
  styleUrl: './display.component.scss'
})
export class DisplayComponent implements OnInit {
    kiosk!: Kiosk;
    timeline?: Timeline;
    screens: Map<number, screenDP> = new Map<number, screenDP>;
    screensNextKey: number = 0;

    refreshKioskTimer = timer(1000, 1000);
    refreshKioskTimerSubscription: Subscription | undefined;
    activateScreenTimerSubscription: Subscription | undefined;
    loadNextScreenTimerSubscription: Subscription | undefined;

    showMissingName: boolean = false;

    constructor(
        private kioskService: KioskService,
        private timelineService: TimelineService,
        private screenService: ScreenService
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
                    if (this.timeline == undefined || this.timeline != timeline) {
                        this.timeline = timeline;
                        this.timeline.current_pos = ((Math.ceil(this.timeline.current_pos / 2) - 1) % this.timeline.screen_ids.length) * 2;
                        this.screens.clear();
                        this.screensNextKey = 0;
                        this.loadNextScreen();
                    }
                    else {
                        this.timeline = timeline;
                    }
                });
    }

    sendCurrentPos(pos: number) {
        if (this.timeline) {
            this.timeline.current_pos = pos;
            this.timeline.kiosk_id = this.kiosk.id;
            this.timelineService.setCurrentPos(this.timeline).subscribe(() => {});
        }
    }

    loadNextScreen(forceActivate: boolean = false) {
        this.loadNextScreenTimerSubscription?.unsubscribe();
        if (this.timeline) {
            let load_pos = Math.floor((this.timeline.current_pos / 2) + 1) % this.timeline.screen_ids.length;
            this.screenService
                .getScreen(this.timeline.screen_ids[load_pos])
                .subscribe((screen: Screen) => {
                    let sdp: screenDP = <screenDP>{screen: screen, active: false, startTS: null};
                    this.screens.set(this.screensNextKey, sdp);
                    this.screensNextKey = this.screensNextKey + 1;
                    this.sendCurrentPos(load_pos * 2);
                    if (this.screens.size == 1) this.activateNextScreen();
                    else {
                        if (forceActivate) this.activateNextScreen();
                        else if (this.screens.has(this.screensNextKey - 2)) {
                            let csdp: screenDP = this.screens.get(this.screensNextKey - 2)!;
                            if (csdp.screen.duration && csdp.startTS) {
                                let target: Date = new Date((csdp.startTS + csdp.screen.duration) * 1000);
                                this.activateScreenTimerSubscription = timer(target).subscribe(() => this.activateNextScreen(target));
                            }
                        }
                    }
                });
        }
    }

    activateNextScreen(startTime: Date | null = null) {
        let currentTS: number = startTime ? (startTime.getTime() / 1000) : (Date.now() / 1000);
        let nowScreenDP: screenDP | undefined = this.screens.get(this.screensNextKey - 1);
        if (nowScreenDP) {
            nowScreenDP.startTS = currentTS;
            nowScreenDP.active = true;
            this.screens.set(this.screensNextKey - 1, nowScreenDP);
        }
        if (this.screens.has(this.screensNextKey - 2)) this.screens.delete(this.screensNextKey - 2);
        this.activateScreenTimerSubscription?.unsubscribe();
        if (nowScreenDP) {
            if (this.timeline) this.sendCurrentPos(this.timeline.current_pos + 1);
            if (nowScreenDP.screen.duration) {
                let target: Date = new Date((currentTS + nowScreenDP.screen.duration - 2) * 1000);
                this.loadNextScreenTimerSubscription = timer(target).subscribe(() => this.loadNextScreen());
            }
        }
    }
}
