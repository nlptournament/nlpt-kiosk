import { Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';

import { MenuItem } from 'primeng/api';
import { MenubarModule } from 'primeng/menubar';
import { TooltipModule } from 'primeng/tooltip';

import { User } from '../../../interfaces/user';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { Kiosk } from '../../../interfaces/kiosk';
import { Timeline } from '../../../interfaces/timeline';
import { Screen } from '../../../interfaces/screen';
import { Media } from '../../../interfaces/media';

import { ErrorHandlerService } from '../../../services/error-handler.service';
import { PresentationService } from '../../../services/presentation.service';
import { KioskService } from '../../../services/kiosk.service';
import { UserService } from '../../../services/user.service';
import { ScreenTemplateService } from '../../../services/screen-template.service';
import { ScreenService } from '../../../services/screen.service';
import { TimelineService } from '../../../services/timeline.service';
import { TimelineTemplateService } from '../../../services/timeline-template.service';
import { MediaService } from '../../../services/media.service';

import { KioskComponent } from '../../elements/kiosk/kiosk.component';
import { ProfilePanelComponent } from '../../admin/profile-panel/profile-panel.component';
import { UpdatePwComponent } from '../../admin/update-pw/update-pw.component';
import { WebSocketService } from '../../../services/web-socket.service';

@Component({
  selector: 'app-presenter-screen',
  imports: [CommonModule, MenubarModule, KioskComponent, TooltipModule, ProfilePanelComponent, UpdatePwComponent],
  templateUrl: './presenter-screen.component.html',
  styleUrl: './presenter-screen.component.scss'
})
export class PresenterScreenComponent implements OnInit {
    menuItems: MenuItem[] = [];
    currentUser!: User;
    users: Map<string, User> = new Map<string, User>;
    screenTemplates: Map<string, ScreenTemplate> = new Map<string, ScreenTemplate>;
    screens: Map<string, Screen> = new Map<string, Screen>;
    timelineTemplates: Map<string, TimelineTemplate> = new Map<string, TimelineTemplate>;
    kiosks: Map<string, Kiosk> = new Map<string, Kiosk>;
    timelines: Map<string, Timeline> = new Map<string, Timeline>;
    medias: Map<string, Media> = new Map<string, Media>;

    wssSubscription: Subscription | undefined;

    showHiddenKiosks: boolean = false;
    updatePwActive: boolean = false;
    panelProfileActive: boolean = false;
    timelinesChanged: boolean = false;
    bigButtons: boolean = false;

    constructor(
        private errorHandler: ErrorHandlerService,
        private router: Router,
        private presentationService: PresentationService,
        private userService: UserService,
        private screenTemplateService: ScreenTemplateService,
        private screenService: ScreenService,
        private timelinetemplateService: TimelineTemplateService,
        private kioskService: KioskService,
        private timelineService: TimelineService,
        private mediaService: MediaService,
        private websocketService: WebSocketService,
    ) { }

    ngOnInit(): void {
        this.wssSubscription = this.websocketService.getAdminMessages().subscribe((msg) => this.wssRx(msg));
        this.populateMenu();
        this.refreshUsers();
        this.refreshScreenTemplates();
        this.refreshScreens();
        this.refreshTimelineTemplates();
        this.refreshKiosks();
        this.refreshTimelines();
        this.refreshMedia();
    }

    wssRx(msg: any) {
        if (Object.keys(msg).includes('content')) {
            if (Object.keys(msg).includes('kiosk')) {
                let kiosk: Kiosk = <Kiosk>msg['kiosk'];
                if (kiosk.id && msg['content'] == 'update') {
                    this.kiosks.set(kiosk.id, kiosk);
                    this.setKiosksSorted();
                }
                else if (kiosk.id && this.kiosks.has(kiosk.id) && msg['content'] == 'delete')
                    this.kiosks.delete(kiosk.id);
            }
            if (Object.keys(msg).includes('timeline')) {
                let tl: Timeline = <Timeline>msg['timeline'];
                if (tl.id && msg['content'] == 'update' && !tl.preset)
                    this.timelines.set(tl.id, tl);
                else if (tl.id && this.timelines.has(tl.id) && (msg['content'] == 'delete' || tl.preset))
                    this.timelines.delete(tl.id);
                this.timelinesChanged = !this.timelinesChanged;
            }
            if (Object.keys(msg).includes('screen')) {
                let screen: Screen = <Screen>msg['screen'];
                if (screen.id && msg['content'] == 'update')
                    this.screens.set(screen.id, screen);
                else if (screen.id && this.screens.has(screen.id) && msg['content'] == 'delete') {
                    this.screens.delete(screen.id);
                    this.refreshScreenTemplates();
                }
            }
            if (Object.keys(msg).includes('timelinetemplate')) {
                let timelinetemplate: TimelineTemplate = <TimelineTemplate>msg['timelinetemplate'];
                if (timelinetemplate.id && msg['content'] == 'update')
                    this.timelineTemplates.set(timelinetemplate.id, timelinetemplate);
                else if (timelinetemplate.id && this.timelineTemplates.has(timelinetemplate.id) && msg['content'] == 'delete')
                    this.timelineTemplates.delete(timelinetemplate.id);
            }
            if (Object.keys(msg).includes('user')) {
                let user: User = <User>msg['user'];
                if (user.id && msg['content'] == 'update') {
                    this.users.set(user.id, user);
                    if (this.currentUser.id == user.id) this.currentUser = user;
                }
                else if (user.id && this.users.has(user.id) && msg['content'] == 'delete')
                    this.users.delete(user.id);
            }
            if (Object.keys(msg).includes('media')) {
                let media: Media = <Media>msg['media'];
                if (media.id && msg['content'] == 'update')
                    this.medias.set(media.id, media);
                else if (media.id && this.medias.has(media.id) && msg['content'] == 'delete')
                    this.medias.delete(media.id);
            }
        }
    }

    populateMenu() {
        this.menuItems = [
            {
                label: 'User',
                icon: 'pi pi-user',
                items: [
                    {
                        label: this.currentUser?.login,
                        disabled: true
                    },
                    {
                        label: 'Change Password',
                        icon: 'pi pi-key',
                        command: () => {
                            this.updatePwActive = true;
                        }
                    },
                    {
                        label: 'Profile',
                        icon: 'pi pi-cog',
                        command: () => {
                            this.panelProfileActive = true;
                        }
                    },
                    {
                        label: 'Show hidden Kiosks',
                        icon: 'pi pi-eye',
                        visible: !this.showHiddenKiosks,
                        command: () => {
                            this.showHiddenKiosks = true;
                            this.populateMenu();
                        }
                    },
                    {
                        label: 'Suppress hidden Kiosks',
                        icon: 'pi pi-eye-slash',
                        visible: this.showHiddenKiosks,
                        command: () => {
                            this.showHiddenKiosks = false;
                            this.populateMenu();
                        }
                    },
                    {
                        label: 'Show big Buttons',
                        icon: 'pi pi-arrow-up-right-and-arrow-down-left-from-center',
                        visible: !this.bigButtons,
                        command: () => {
                            this.bigButtons = true;
                            this.populateMenu();
                        }
                    },
                    {
                        label: 'Show small Buttons',
                        icon: 'pi pi-arrow-down-left-and-arrow-up-right-to-center',
                        visible: this.bigButtons,
                        command: () => {
                            this.bigButtons = false;
                            this.populateMenu();
                        }
                    },
                    {
                        separator: true
                    },
                    {
                        label: 'Admin Interface',
                        icon: 'pi pi-hammer',
                        command: () => {
                            this.router.navigate(['/admin']);
                        }
                    },
                    {
                        separator: true
                    },
                    {
                        label: 'Logout',
                        icon: 'pi pi-sign-out',
                        command: () => {
                            this.router.navigate(['/logout']);
                        }
                    },
                ]
            },
        ]
    }

    execForward() {
        this.presentationService.execForward().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    execBackward() {
        this.presentationService.execBackward().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    execRestart() {
        this.presentationService.execRestart().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    refreshUsers(): void {
        this.userService.getMe().subscribe({
            next: (user: User) => {
                this.currentUser = user;
            },
            error: (error: HttpErrorResponse) => {
                this.errorHandler.handleError(error);
            }
        });
        this.userService.getUsers().subscribe({
            next: (users: User[]) => {
                let ul: Map<string, User> = new Map<string, User>;
                for (let user of users) if (user.id) ul.set(user.id, user);
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
                    this.setKiosksSorted(kl);
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    setKiosksSorted(kiosks: Map<string, Kiosk> = this.kiosks) {
        this.kiosks = new Map<string, Kiosk>(
            [...kiosks].sort((a, b) => (
                (a[1].common == b[1].common) ? a[1].desc.localeCompare(b[1].desc) : (
                    (a[1].common ? -1 : 1)
                )
            )
        ));
    }

    refreshTimelines() {
        this.timelineService
            .getTimelines()
            .subscribe({
                next: (tls: Timeline[]) => {
                    let tll: Map<string, Timeline> = new Map<string, Timeline>;
                    for (let tl of tls) if (tl.id && !tl.preset) tll.set(tl.id, tl);
                    this.timelines = tll;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    refreshMedia() {
        this.mediaService
            .getMedias()
            .subscribe({
                next: (medias: Media[]) => {
                    let ml: Map<string, Media> = new Map<string, Media>;
                    for (let m of medias) if (m.id) ml.set(m.id, m);
                    this.medias = ml;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }
}
