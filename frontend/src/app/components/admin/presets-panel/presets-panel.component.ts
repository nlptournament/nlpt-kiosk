import { Component, input, model, OnInit, output } from '@angular/core';

import { Preset } from '../../../interfaces/preset';
import { Timeline } from '../../../interfaces/timeline';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { Media } from '../../../interfaces/media';

import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { PresetComponent } from '../../elements/preset/preset.component';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { TooltipModule } from 'primeng/tooltip';

import { Kiosk } from '../../../interfaces/kiosk';
import { TimelineService } from '../../../services/timeline.service';

interface selectableUser {
    code: string | null;
    name: string;
}

@Component({
  selector: 'panel-presets',
  imports: [CommonModule, Dialog, PresetComponent, FormsModule, SelectModule, InputTextModule, TooltipModule],
  templateUrl: './presets-panel.component.html',
  styleUrl: './presets-panel.component.scss'
})
export class PresetsPanelComponent implements OnInit {
    presets = input.required<Map<string, Preset>>();
    kiosks = input.required<Map<string, Kiosk>>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    medias = input.required<Map<string, Media>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    timelines: Map<string, Timeline> = new Map<string, Timeline>;
    selectableUsers: selectableUser[] = [];

    showHiddenPresets: boolean = false;
    filterDesc: string = "";
    filterUser: string | null = null;
    filterUserEqual: boolean = true;
    filterCommon: boolean | null = null;

    constructor(
        private timelineService: TimelineService
    ) { }

    ngOnInit(): void {
        this.refreshTimelines();
        this.createSelectableUsers();
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        su.push(<selectableUser>{code: null, name: 'user'})
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login})
        }
        this.selectableUsers = su;
    }

    refreshTimelines() {
        let tll: Map<string, Timeline> = new Map<string, Timeline>;
        this.timelineService
            .getTimelines()
            .subscribe({
                next: (timelines: Timeline[]) => {
                    for (let tl of timelines) {
                        if (tl.preset && tl.id) tll.set(tl.id, tl);
                    }
                }
            });
        this.timelines = tll;
    }

    closeDialog() {
        this.isActive.set(false);
    }
}
