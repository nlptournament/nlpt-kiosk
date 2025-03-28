import { Component, effect, input, OnInit, output } from '@angular/core';
import { User } from '../../../interfaces/user';
import { Kiosk } from '../../../interfaces/kiosk';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { CommonModule } from '@angular/common';
import { KioskService } from '../../../services/kiosk.service';
import { Dialog } from 'primeng/dialog';
import { IftaLabelModule } from 'primeng/iftalabel';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { SelectButtonModule } from 'primeng/selectbutton';
import { ButtonModule } from 'primeng/button';
import { Timeline } from '../../../interfaces/timeline';
import { TimelineComponent } from '../timeline/timeline.component';
import { TimelineService } from '../../../services/timeline.service';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { Screen } from '../../../interfaces/screen';

interface selectableCommon {
    code: boolean,
    name: string
}

interface selectableUser {
    code: string;
    name: string;
}

interface selectableTimelineTemplate {
    code: string;
    name: string;
}

@Component({
  selector: 'element-kiosk',
  imports: [CommonModule, TimelineComponent, Dialog, FormsModule, IftaLabelModule, InputTextModule, SelectModule, SelectButtonModule, ButtonModule],
  templateUrl: './kiosk.component.html',
  styleUrl: './kiosk.component.scss'
})
export class KioskComponent implements OnInit {
    kiosk = input.required<Kiosk>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    timelines = input.required<Map<string, Timeline>>();
    timelinesChanged = input<boolean>(false);
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    editResult = output<string|null|undefined>();
    timelineEdited = output<string|null|undefined>();

    relevantTimelines: Timeline[] = [];
    editActive: boolean = false;
    selectableCommons: selectableCommon[] = [];
    selectableUsers: selectableUser[] = [];
    selectableTimelineTemplates: selectableTimelineTemplate[] = [];
    timelineCreateActive: boolean = false;
    selectedTimelineTemplate: string = "";

    constructor (
        private kioskService: KioskService,
        private timelineService: TimelineService
    ) {
        effect(() => {
            if ((this.timelinesChanged() || !this.timelinesChanged()) && this.timelines() && this.kiosk()) this.refreshTimelines();
        });
    }

    ngOnInit(): void {
        this.selectableCommons.push(<selectableCommon>{code: true, 'name': 'available2everyone'});
        this.selectableCommons.push(<selectableCommon>{code: false, 'name': 'just4owner'});
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login})
        }
        this.selectableUsers = su;
    }

    createSelectableTimelineTemplates() {
        let stt: selectableTimelineTemplate[] = [];
        for (let k of this.timelineTemplates().keys()) {
            stt.push(<selectableTimelineTemplate>{code: k, name: this.timelineTemplates().get(k)!.desc})
        }
        this.selectableTimelineTemplates = stt;
    }

    refreshTimelines() {
        console.log('refresh');
        let rt: Timeline[] = [];
        for (let tl of this.timelines().values()) {
            if (tl.kiosk_id === this.kiosk().id && tl.id !== this.kiosk().timeline_id)
                rt.push(tl);
        }
        this.relevantTimelines = rt;
    }

    kioskAccept() {
        this.kiosk().added_by_id = this.currentUser().id;
        this.kioskSave();
    }

    kioskDelete() {
        this.kioskService
            .deleteKiosk(this.kiosk().id)
            .subscribe((result: any) => {
                next: this.editResult.emit(this.kiosk().id);
            });
    }

    kioskSave() {
        this.kioskService
            .updateKiosk(this.kiosk())
            .subscribe((result: any) => {
                next: {
                    if (this.editActive) this.editClose();
                    else this.editResult.emit(this.kiosk().id);
                }
            });
    }

    editOpen() {
        this.createSelectableUsers();
        this.editActive = true;
    }

    editClose() {
        if (this.editActive) {
            this.editResult.emit(this.kiosk().id);
            this.editActive = false;
        }
    }

    timelineCreateActivate() {
        this.createSelectableTimelineTemplates();
        this.selectedTimelineTemplate = "";
        this.timelineCreateActive = true;
    }

    timelineCreate() {
        if (this.timelineTemplates().has(this.selectedTimelineTemplate)) {
            let tt: TimelineTemplate = this.timelineTemplates().get(this.selectedTimelineTemplate)!;
            let tl: Timeline = <Timeline>{template_id: tt.id, kiosk_id: this.kiosk().id, screen_ids: tt.screen_ids};
            this.timelineService
                .createTimeline(tl)
                .subscribe((result: any) => {
                    next: {
                        if (Object.keys(result).includes('created')) {
                            this.timelineEdited.emit(result['created']);
                        }
                    }
                });
        }
        this.timelineCreateActive = false;
    }
}
