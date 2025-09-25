import { Component, input, OnInit, output } from '@angular/core';

import { Preset } from '../../../interfaces/preset';
import { Kiosk } from '../../../interfaces/kiosk';
import { Timeline } from '../../../interfaces/timeline';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { Media } from '../../../interfaces/media';

import { TimelineComponent } from '../timeline/timeline.component';

import { PresetService } from '../../../services/preset.service';
import { UserService } from '../../../services/user.service';
import { TimelineService } from '../../../services/timeline.service';
import { KioskService } from '../../../services/kiosk.service';

import { Dialog } from 'primeng/dialog';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TooltipModule } from 'primeng/tooltip';
import { IftaLabelModule } from 'primeng/iftalabel';
import { ButtonModule } from 'primeng/button';
import { SelectButtonModule } from 'primeng/selectbutton';
import { ProgressSpinnerModule } from 'primeng/progressspinner';

interface selectableUser {
    code: string;
    name: string;
}

interface selectableCommon {
    code: boolean,
    name: string
}

@Component({
  selector: 'element-preset',
  imports: [CommonModule, Dialog, FormsModule, TooltipModule, IftaLabelModule, SelectModule, InputTextModule, TimelineComponent, ButtonModule, SelectButtonModule, ProgressSpinnerModule],
  templateUrl: './preset.component.html',
  styleUrl: './preset.component.scss'
})
export class PresetComponent implements OnInit {
    preset = input.required<Preset>();
    kiosks = input.required<Map<string, Kiosk>>();
    timelines = input.required<Map<string, Timeline>>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    medias = input.required<Map<string, Media>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    editResult = output<string|null|undefined>();

    relevantTimelines: Map<string, Timeline[]> = new Map<string, Timeline[]>;
    editActive: boolean = false;
    waitingActive: boolean = false;
    timelinesExpanded: boolean = false;
    selectableUsers: selectableUser[] = [];
    selectableCommons: selectableCommon[] = [];

    constructor(
        private presetService: PresetService,
        private userService: UserService,
        private timelineService: TimelineService,
        private kioskService: KioskService
    ) { }

    ngOnInit(): void {
        this.selectableCommons.push(<selectableCommon>{code: true, 'name': 'available2everyone'});
        this.selectableCommons.push(<selectableCommon>{code: false, 'name': 'just4owner'});
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login});
        }
        this.selectableUsers = su;
    }

    refreshTimelines() {
        let rt: Map<string, Timeline[]> = new Map<string, Timeline[]>;
        for (let tlid of this.preset().timeline_ids) {
            if (this.timelines().has(tlid)) {
                let tl: Timeline = this.timelines().get(tlid)!;
                if (tl.kiosk_id) {
                    if (rt.has(tl.kiosk_id)) rt.get(tl.kiosk_id)!.push(tl);
                    else {
                        let tll: Timeline[] = [];
                        tll.push(tl);
                        rt.set(tl.kiosk_id, tll);
                    }
                }
            }
        }
        this.relevantTimelines = rt;
    }

    timelinesExpand() {
        this.refreshTimelines();
        this.timelinesExpanded = true;
    }

    editOpen() {
        if (!this.editActive) {
            this.createSelectableUsers();
            this.editActive = true;
        }
    }

    editClose() {
        if (this.editActive) {
            this.editResult.emit(this.preset().id);
            this.editActive = false;
        }
    }

    presetDelete() {
        if (this.preset().id)
            this.presetService
                .deletePreset(this.preset().id!)
                .subscribe((result: any) => {
                    this.editResult.emit(this.preset().id);
                });
    }

    presetSave() {
        this.presetService
            .updatePreset(this.preset())
            .subscribe((result: any) => {
                if (this.editActive) this.editClose();
                else this.editResult.emit(this.preset().id);
            });
    }

    presetApply() {
        if (this.preset().id)
            this.presetService
                .applyPreset(this.preset().id!)
                .subscribe((result: any) => {});
    }

    presetApplyToKiosks() {
        if (this.preset().id)
            this.waitingActive = true;
            this.presetService
                .applyPreset(this.preset().id!)
                .subscribe(async (result: any) => {
                    if (Object.keys(result).includes('created')) {
                        let sync_data = {};
                        for (let t_id of result['created']) {
                            this.timelineService.getTimeline(t_id).subscribe((timeline: Timeline) => {
                                if (timeline.kiosk_id)
                                    sync_data = { ...sync_data, [timeline.kiosk_id]: t_id};
                            });
                        }
                        for (let counter: number = 0; counter < 10; counter++) {
                            if (result['created'].length == Object.keys(sync_data).length) break;
                            await this.sleep(500);
                        }
                        this.kioskService.syncedApply(sync_data).subscribe((result: any) => {
                            this.waitingActive = false;
                        });
                    }
                });
    }

    hidePreset() {
        if (this.currentUser().id && this.preset().id) this.userService.addHide(this.currentUser().id!, this.preset().id!).subscribe();
    }

    unhidePreset() {
        if (this.currentUser().id && this.preset().id) this.userService.delHide(this.currentUser().id!, this.preset().id!).subscribe();
    }

    private sleep(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
