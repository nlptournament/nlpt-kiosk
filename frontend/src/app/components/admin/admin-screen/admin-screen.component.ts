import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule, Time } from '@angular/common';

import { Kiosk, KioskTlSelection } from '../../../interfaces/kiosk';
import { User } from '../../../interfaces/user';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { Screen } from '../../../interfaces/screen';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { Timeline } from '../../../interfaces/timeline';
import { Preset } from '../../../interfaces/preset';

import { KioskService } from '../../../services/kiosk.service';
import { UserService } from '../../../services/user.service';
import { ScreenTemplateService } from '../../../services/screen-template.service';
import { ScreenService } from '../../../services/screen.service';
import { TimelineService } from '../../../services/timeline.service';
import { TimelineTemplateService } from '../../../services/timeline-template.service';
import { PresetService } from '../../../services/preset.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';

import { KioskComponent } from '../../elements/kiosk/kiosk.component';
import { ScreensPanelComponent } from '../screens-panel/screens-panel.component';
import { TimelineTemplatesPanelComponent } from '../timeline-templates-panel/timeline-templates-panel.component';
import { PresetsPanelComponent } from '../presets-panel/presets-panel.component';
import { UpdatePwComponent } from '../update-pw/update-pw.component';

import { MenuItem } from 'primeng/api';
import { MenubarModule } from 'primeng/menubar';
import { Subscription } from 'rxjs';
import { WebSocketService } from '../../../services/web-socket.service';


@Component({
  selector: 'app-admin-screen',
  imports: [CommonModule, MenubarModule, KioskComponent, ScreensPanelComponent, TimelineTemplatesPanelComponent, PresetsPanelComponent, UpdatePwComponent],
  templateUrl: './admin-screen.component.html',
  styleUrl: './admin-screen.component.scss'
})
export class AdminScreenComponent implements OnInit, OnDestroy {
    menuItems: MenuItem[] = [];
    currentUser!: User;
    users: Map<string, User> = new Map<string, User>;
    screenTemplates: Map<string, ScreenTemplate> = new Map<string, ScreenTemplate>;
    screens: Map<string, Screen> = new Map<string, Screen>;
    timelineTemplates: Map<string, TimelineTemplate> = new Map<string, TimelineTemplate>;
    kiosks: Map<string, Kiosk> = new Map<string, Kiosk>;
    timelines: Map<string, Timeline> = new Map<string, Timeline>;
    presets: Map<string, Preset> = new Map<string, Preset>;

    wssSubscription: Subscription | undefined;

    panelScreensActive: boolean = false;
    panelTimelineTemplatesActive: boolean = false;
    panelPresetsActive: boolean = false;
    updatePwActive: boolean = false;
    timelinesChanged: boolean = false;
    selectedNextTimelines: Map<string, string> = new Map<string, string>;
    selectedPresetTimelines: Map<string, string[]> = new Map<string, string[]>;

    constructor(
        private errorHandler: ErrorHandlerService,
        private websocketService: WebSocketService,
        private router: Router,
        private userService: UserService,
        private screenTemplateService: ScreenTemplateService,
        private screenService: ScreenService,
        private timelinetemplateService: TimelineTemplateService,
        private kioskService: KioskService,
        private timelineService: TimelineService,
        private presetService: PresetService
    ) { }

    ngOnInit(): void {
        this.populateMenu();
        this.refreshUsers();
        this.refreshScreenTemplates();
        this.refreshScreens();
        this.refreshTimelineTemplates();
        this.refreshKiosks();
        this.refreshTimelines();
        this.refreshPresets();
        this.wssSubscription = this.websocketService.getMessages().subscribe((msg) => this.wssRx(msg));
    }

    ngOnDestroy(): void {
        this.wssSubscription?.unsubscribe();
        this.websocketService.closeConnection();
    }

    wssRx(msg: any) {
        if (Object.keys(msg).includes('content')) {
            if (Object.keys(msg).includes('kiosk')) {
                let kiosk: Kiosk = <Kiosk>msg['kiosk'];
                if (kiosk.id && msg['content'] == 'update')
                    this.kiosks.set(kiosk.id, kiosk);
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
            if (Object.keys(msg).includes('preset')) {
                let preset: Preset = <Preset>msg['preset'];
                if (preset.id && msg['content'] == 'update')
                    this.presets.set(preset.id, preset);
                else if (preset.id && this.presets.has(preset.id) && msg['content'] == 'delete')
                    this.presets.delete(preset.id);
            }
            if (Object.keys(msg).includes('timelinetemplate')) {
                let timelinetemplate: TimelineTemplate = <TimelineTemplate>msg['timelinetemplate'];
                if (timelinetemplate.id && msg['content'] == 'update')
                    this.timelineTemplates.set(timelinetemplate.id, timelinetemplate);
                else if (timelinetemplate.id && this.timelineTemplates.has(timelinetemplate.id) && msg['content'] == 'delete')
                    this.timelineTemplates.delete(timelinetemplate.id);
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
                        label: 'Logout',
                        icon: 'pi pi-sign-out',
                        command: () => {
                            this.router.navigate(['/logout']);
                        }
                    },
                    {
                        label: 'Change Password',
                        icon: 'pi pi-key',
                        command: () => {
                            this.updatePwActive = true;
                        }
                    },
                    {
                        label: 'Manage Users',
                        icon: 'pi pi-users',
                        disabled: true,
                        visible: this.currentUser?.admin,
                        command: () => {
                            this.syncedCurrentTimelineApply();
                        }
                    }
                ]
            },
            {
                label: 'Manage Screens',
                icon: 'pi pi-file',
                command: () => {
                    this.panelScreensActive = true;
                }
            },
            {
                label: 'Manage Timelines',
                icon: 'pi pi-folder',
                command: () => {
                    this.panelTimelineTemplatesActive = true;
                }
            },
            {
                label: 'Manage Presets',
                icon: 'pi pi-list',
                disabled: this.presets.size == 0,
                command: () => {
                    this.panelPresetsActive = true;
                }
            },
            {
                label: 'Create Preset',
                icon: 'pi pi-clipboard',
                disabled: this.selectedPresetTimelines.size == 0,
                command: () => {
                    this.createPresetFromSelection();
                }
            },
            {
                label: 'Synced Apply',
                icon: 'pi pi-desktop',
                disabled: this.selectedNextTimelines.size < 2,
                command: () => {
                    this.syncedCurrentTimelineApply();
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

    refreshPresets() {
        this.presetService
            .getPresets()
            .subscribe({
                next: (presets: Preset[]) => {
                    let pl: Map<string, Preset> = new Map<string, Preset>;
                    for (let p of presets) if (p.id) pl.set(p.id, p);
                    this.presets = pl;
                    this.populateMenu();
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    timelinesSelected(event: KioskTlSelection) {
        if (event.next) this.selectedNextTimelines.set(event.kiosk_id, event.next);
        else if (this.selectedNextTimelines.has(event.kiosk_id)) this.selectedNextTimelines.delete(event.kiosk_id);

        if (event.preset.length > 0) this.selectedPresetTimelines.set(event.kiosk_id, event.preset);
        else if (this.selectedPresetTimelines.has(event.kiosk_id)) this.selectedPresetTimelines.delete(event.kiosk_id);

        this.populateMenu();
    }

    syncedCurrentTimelineApply() {
        let data = {};
        for (let kiosk_id of this.selectedNextTimelines.keys()) {
            let timeline_id: string = this.selectedNextTimelines.get(kiosk_id)!;
            data = { ...data, [kiosk_id]: timeline_id};
        }
        this.kioskService
            .syncedApply(data)
            .subscribe((result: any) => {
                this.selectedNextTimelines.clear();
                this.populateMenu();
            });
    }

    createPresetFromSelection() {
        let preset: Preset = <Preset>{id: null, user_id: this.currentUser.id, timeline_ids: <string[]>[], desc: '', common: false};
        for (let timeline_ids of this.selectedPresetTimelines.values()) {
            for (let tlid of timeline_ids) {
                preset.timeline_ids.push(tlid);
            }
        }
        this.presetService
            .createPreset(preset)
            .subscribe({
                next: (result: any) => {
                   this.selectedPresetTimelines.clear();
                   this.populateMenu();
                }
            });
    }

}
