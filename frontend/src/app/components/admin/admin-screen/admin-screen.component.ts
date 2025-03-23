import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';

import { Kiosk } from '../../../interfaces/kiosk';
import { User } from '../../../interfaces/user';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { Screen } from '../../../interfaces/screen';
import { TimelineTemplate } from '../../../interfaces/timeline-template';

import { KioskService } from '../../../services/kiosk.service';
import { UserService } from '../../../services/user.service';
import { ScreenTemplateService } from '../../../services/screen-template.service';
import { ScreenService } from '../../../services/screen.service';
import { TimelineTemplateService } from '../../../services/timeline-template.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';

import { KioskComponent } from '../../elements/kiosk/kiosk.component';
import { ScreensPanelComponent } from '../screens-panel/screens-panel.component';
import { TimelineTemplatesPanelComponent } from '../timeline-templates-panel/timeline-templates-panel.component';

import { MenuItem } from 'primeng/api';
import { SpeedDial } from 'primeng/speeddial';

@Component({
  selector: 'app-admin-screen',
  imports: [CommonModule, SpeedDial, KioskComponent, ScreensPanelComponent, TimelineTemplatesPanelComponent],
  templateUrl: './admin-screen.component.html',
  styleUrl: './admin-screen.component.scss'
})
export class AdminScreenComponent implements OnInit {
    menuItems: MenuItem[] = [];
    currentUser!: User;
    users: Map<string, User> = new Map<string, User>;
    screenTemplates: Map<string, ScreenTemplate> = new Map<string, ScreenTemplate>;
    screens: Map<string, Screen> = new Map<string, Screen>;
    timelineTemplates: Map<string, TimelineTemplate> = new Map<string, TimelineTemplate>;
    kiosks: Map<string, Kiosk> = new Map<string, Kiosk>;

    panelScreensActive: boolean = false;
    panelTimelineTemplatesActive: boolean = false;

    constructor(
        private errorHandler: ErrorHandlerService,
        private router: Router,
        private userService: UserService,
        private screenTemplateService: ScreenTemplateService,
        private screenService: ScreenService,
        private timelinetemplateService: TimelineTemplateService,
        private kioskService: KioskService
    ) { }

    ngOnInit(): void {
        this.populateMenu();
        this.refreshUsers();
        this.refreshScreenTemplates();
        this.refreshScreens();
        this.refreshTimelineTemplates();
        this.refreshKiosks();
    }

    populateMenu() {
        this.menuItems = [
            {
                label: 'Logout',
                icon: 'pi pi-sign-out',
                command: () => {
                    this.router.navigate(['/logout']);
                }
            },
            {
                label: 'Manage Screens',
                icon: 'pi pi-file',
                command: () => {
                    this.panelScreensActive = true;
                }
            },
            {
                label: 'Manage Timeline Templates',
                icon: 'pi pi-folder',
                command: () => {
                    this.panelTimelineTemplatesActive = true;
                }
            }
        ]
    }

    refreshUsers() {
        this.userService
            .getMe()
            .subscribe({
                next: (user: User) => {
                    this.currentUser = user;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
        this.userService
            .getUsers()
            .subscribe({
                next: (users: User[]) => {
                    let ul: Map<string, User> = new Map<string, User>;
                    for (let user of users) ul.set(user.id, user);
                    this.users = ul;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    refreshScreenTemplates() {
        this.screenTemplateService
            .getScreenTemplates()
            .subscribe({
                next: (sts: ScreenTemplate[]) => {
                    let stl: Map<string, ScreenTemplate> = new Map<string, ScreenTemplate>;
                    for (let st of sts) stl.set(st.id, st);
                    this.screenTemplates = stl;
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

    refreshTimelineTemplates() {
        this.timelinetemplateService
            .getTimelineTemplates()
            .subscribe({
                next: (tts: TimelineTemplate[]) => {
                    let ttl: Map<string, TimelineTemplate> = new Map<string, TimelineTemplate>;
                    for (let tt of tts) if (tt.id) ttl.set(tt.id, tt);
                    this.timelineTemplates = ttl;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
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

    screenEdited(event: string|null|undefined) {
        if (event) {
            this.screenService
                .getScreen(event)
                .subscribe({
                    next: (screen: Screen) => {
                        if (screen.id) this.screens.set(screen.id, screen);
                    },
                    error: (err: HttpErrorResponse) => {
                        if (err.status == 404 && this.screens.has(event)) {
                            this.refreshTimelineTemplates();
                            this.screens.delete(event);
                        }
                        else
                            this.errorHandler.handleError(err);
                    }
                });
        }
    }

    timelineTemplateEdited(event: string|null|undefined) {
        if (event) {
            this.timelinetemplateService
                .getTimelineTemplate(event)
                .subscribe({
                    next: (tt: TimelineTemplate) => {
                        if (tt.id) this.timelineTemplates.set(tt.id, tt);
                    },
                    error: (err: HttpErrorResponse) => {
                        if (err.status == 404 && this.timelineTemplates.has(event))
                            this.timelineTemplates.delete(event);
                        else
                            this.errorHandler.handleError(err);
                    }
                });
        }
    }

    kioskEdited(event: string|null|undefined) {
        if (event) {
            this.kioskService
                .getKiosk(event)
                .subscribe({
                    next: (kiosk: Kiosk) => {
                        if (kiosk.id) this.kiosks.set(kiosk.id, kiosk);
                    },
                    error: (err: HttpErrorResponse) => {
                        if (err.status == 404 && this.kiosks.has(event))
                            this.kiosks.delete(event);
                        else
                            this.errorHandler.handleError(err);
                    }
                });
        }
    }

}
