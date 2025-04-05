import { Component, input, OnInit, output } from '@angular/core';

import { Preset } from '../../../interfaces/preset';
import { Kiosk } from '../../../interfaces/kiosk';
import { Timeline } from '../../../interfaces/timeline';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { TimelineTemplate } from '../../../interfaces/timeline-template';

import { TimelineComponent } from '../timeline/timeline.component';

import { PresetService } from '../../../services/preset.service';
import { Dialog } from 'primeng/dialog';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TooltipModule } from 'primeng/tooltip';
import { IftaLabelModule } from 'primeng/iftalabel';
import { ButtonModule } from 'primeng/button';
import { SelectButtonModule } from 'primeng/selectbutton';

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
  imports: [CommonModule, Dialog, FormsModule, TooltipModule, IftaLabelModule, SelectModule, InputTextModule, TimelineComponent, ButtonModule, SelectButtonModule],
  templateUrl: './preset.component.html',
  styleUrl: './preset.component.scss'
})
export class PresetComponent implements OnInit {
    preset = input.required<Preset>();
    kiosks = input.required<Map<string, Kiosk>>();
    timelines = input.required<Map<string, Timeline>>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    editResult = output<string|null|undefined>();
    timelineEdited = output<string|null|undefined>();

    relevantTimelines: Map<string, Timeline[]> = new Map<string, Timeline[]>;
    editActive: boolean = false;
    timelinesExpanded: boolean = false;
    selectableUsers: selectableUser[] = [];
    selectableCommons: selectableCommon[] = [];

    constructor(
        private presetService: PresetService
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
                .subscribe((result: any) => {
                    if (Object.keys(result).includes('created')) {
                        for (let tlid of result['created']) {
                            this.timelineEdited.emit(tlid);
                        }
                    }
                });
    }
}
