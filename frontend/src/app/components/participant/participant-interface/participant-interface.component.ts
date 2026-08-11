import { Component, OnDestroy, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Subscription } from 'rxjs';

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
    imports: [],
    templateUrl: './participant-interface.component.html',
    styleUrl: './participant-interface.component.scss'
})
export class ParticipantInterfaceComponent implements OnInit, OnDestroy {
    screens: Map<string, Screen> = new Map<string, Screen>;
    kiosks: Map<string, Kiosk> = new Map<string, Kiosk>;
    streamScreenTemplateId: string = '';

    wssSubscription: Subscription | undefined;

    constructor(
        private errorHandler: ErrorHandlerService,
        private kioskService: KioskService,
        private screenService: ScreenService,
        private screenTemplateService: ScreenTemplateService,
        private websocketService: WebSocketService
    ) {}

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

}
