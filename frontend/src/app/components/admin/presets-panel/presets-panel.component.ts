import { Component, input, model, OnInit, output } from '@angular/core';

import { Preset } from '../../../interfaces/preset';
import { Timeline } from '../../../interfaces/timeline';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { TimelineTemplate } from '../../../interfaces/timeline-template';

import { PresetComponent } from '../../elements/preset/preset.component';

import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { Kiosk } from '../../../interfaces/kiosk';
import { TimelineService } from '../../../services/timeline.service';

@Component({
  selector: 'panel-presets',
  imports: [CommonModule, Dialog, PresetComponent],
  templateUrl: './presets-panel.component.html',
  styleUrl: './presets-panel.component.scss'
})
export class PresetsPanelComponent implements OnInit {
    presets = input.required<Map<string, Preset>>();
    kiosks = input.required<Map<string, Kiosk>>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    timelines: Map<string, Timeline> = new Map<string, Timeline>;

    constructor(
        private timelineService: TimelineService
    ) { }

    ngOnInit(): void {
        this.refreshTimelines();
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
