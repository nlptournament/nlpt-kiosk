import { Component, OnDestroy, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';

import { KioskService } from '../../../services/kiosk.service';
import { ScreenService } from '../../../services/screen.service';
import { WebSocketService } from '../../../services/web-socket.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';

import { Kiosk } from '../../../interfaces/kiosk';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplateService } from '../../../services/screen-template.service';
import { ScreenTemplate } from '../../../interfaces/screen-template';

@Component({
    selector: 'participant-interface',
    imports: [CommonModule],
    templateUrl: './participant-interface.component.html',
    styleUrl: './participant-interface.component.scss'
})
export class ParticipantInterfaceComponent implements OnInit, OnDestroy {
    screens: Map<string, Screen> = new Map<string, Screen>;
    kiosks: Map<string, Kiosk> = new Map<string, Kiosk>;
    streamScreenTemplateId: string = '';
    streamHealth: Map<string, boolean> = new Map<string, boolean>; // media_id -> active status (from WSS stream_health messages)

    wssSubscription: Subscription | undefined;

    constructor(
        private errorHandler: ErrorHandlerService,
        private kioskService: KioskService,
        private screenService: ScreenService,
        private screenTemplateService: ScreenTemplateService,
        private websocketService: WebSocketService
    ) {}

    get activeStreams(): Screen[] {
        if (!this.streamScreenTemplateId) return [];
        const result: Screen[] = [];
        for (const screen of this.screens.values()) {
            if (screen.template_id !== this.streamScreenTemplateId) continue;
            // The stream-player template uses a 'stream' variable slot holding the media_id
            const streamVar = screen.variables?.find((v: any) => v.key === 'stream');
            if (!streamVar?.value) continue;
            // Check health status — only include active streams
            const isActive = this.streamHealth.get(streamVar.value) ?? false;
            if (isActive) {
                result.push(screen);
            }
        }
        return result.sort((a, b) => (a.desc || '').localeCompare(b.desc || ''));
    }

    get participantKiosks(): Kiosk[] {
        const result: Kiosk[] = [];
        for (const kiosk of this.kiosks.values()) {
            if (kiosk.participant === true) {
                result.push(kiosk);
            }
        }
        return result.sort((a, b) => a.name.localeCompare(b.name));
    }

    ngOnInit(): void {
        this.wssSubscription = this.websocketService.getAdminMessages().subscribe((msg) => this.wssRx(msg));
        this.refreshKiosks();
        this.refreshScreens();
        this.fetchStreamScreenTemplateId();
    }

    ngOnDestroy(): void {
        this.wssSubscription?.unsubscribe();
    }

    wssRx(msg: any) {
        if (Object.keys(msg).includes('content')) {
            if (Object.keys(msg).includes('kiosk')) {
                let kiosk: Kiosk = <Kiosk>msg['kiosk'];
                if (kiosk.id && msg['content'] == 'update') {
                    this.kiosks.set(kiosk.id, kiosk);
                }
                else if (kiosk.id && this.kiosks.has(kiosk.id) && msg['content'] == 'delete')
                    this.kiosks.delete(kiosk.id);
            }
            if (Object.keys(msg).includes('screen')) {
                let screen: Screen = <Screen>msg['screen'];
                if (screen.id && msg['content'] == 'update')
                    this.screens.set(screen.id, screen);
                else if (screen.id && this.screens.has(screen.id) && msg['content'] == 'delete') {
                    this.screens.delete(screen.id);
                }
            }
            if (msg['content'] === 'stream_health' && msg['media_id']) {
                this.streamHealth.set(msg['media_id'], msg['active']);
            }
        }
    }

    refreshKiosks() {
        this.kioskService
            .getKiosks()
            .subscribe({
                next: (kiosks: Kiosk[]) => {
                    let kl: Map<string, Kiosk> = new Map<string, Kiosk>;
                    for (let kiosk of kiosks) if (kiosk.id) kl.set(kiosk.id, kiosk);
                    this.kiosks = kl;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    refreshScreens() {
        this.screenService
            .getScreens()
            .subscribe({
                next: (screens: Screen[]) => {
                    let sl: Map<string, Screen> = new Map<string, Screen>;
                    for (let screen of screens) if (screen.id) sl.set(screen.id, screen);
                    this.screens = sl;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    fetchStreamScreenTemplateId() {
        this.screenTemplateService.getScreenTemplates().subscribe({
            next: (screenTemplates: ScreenTemplate[]) => {
                for (let st of screenTemplates) {
                    if (st.key == 'stream-player') {
                        this.streamScreenTemplateId = st.id;
                        break;
                    }
                }
            },
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    openKioskDisplay(name: string): void {
        window.open(`/display?name=${encodeURIComponent(name)}`, '_blank');
    }

    openStream(screenId: string): void {
        // Placeholder — Chapter 3 will implement the viewing strategy (modal or dedicated route)
        console.log('openStream called for screen:', screenId);
    }

}
