import { booleanAttribute, Component, input, OnInit, output } from '@angular/core';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { ScreenComponent } from '../screen/screen.component';
import { ButtonModule } from 'primeng/button';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { CommonModule } from '@angular/common';
import { ListboxModule } from 'primeng/listbox';
import { TimelineTemplateService } from '../../../services/timeline-template.service';

interface selectableUser {
    code: string;
    name: string;
}

interface selectableScreen {
    code: string;
    name: string;
}

@Component({
  selector: 'element-timeline-template',
  imports: [CommonModule, ScreenComponent, ButtonModule, FormsModule, InputTextModule, SelectModule, ListboxModule],
  templateUrl: './timeline-template.component.html',
  styleUrl: './timeline-template.component.scss'
})
export class TimelineTemplateComponent implements OnInit {
    timelineTemplate = input.required<TimelineTemplate>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    editMode = input(false, {transform: booleanAttribute});
    screenEdited = output<string|null|undefined>();
    editResult = output<string|null|undefined>();

    editActive: boolean = false;
    addScreenActive: boolean = false;
    selectableUsers: selectableUser[] = [];
    selectableScreens: selectableScreen[] = [];
    selectedScreen: string = "";

    constructor(
        private ttService: TimelineTemplateService
    ) { }

    ngOnInit(): void {
        if (this.editMode()) this.editActivate();
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login});
        }
        this.selectableUsers = su;
    }

    createSelectableScreens() {
        console.log("Create Selectable Screens");
        let ss: selectableScreen[] = [];
        for (let k of this.screens().keys()) {
            ss.push(<selectableScreen>{code: k, name: this.screens().get(k)!.desc});
        }
        this.selectableScreens = ss;
    }

    screenMoveLeft(index: number) {
        if (this.editActive && index > 0) {
            let tmp: string[] = this.timelineTemplate().screen_ids.splice(index, 1);
            this.timelineTemplate().screen_ids.splice(index-1, 0, tmp[0]);
        }
    }

    screenMoveRight(index: number) {
        if (this.editActive && index < this.timelineTemplate().screen_ids.length - 1) {
            let tmp: string[] = this.timelineTemplate().screen_ids.splice(index, 1);
            this.timelineTemplate().screen_ids.splice(index+1, 0, tmp[0]);
        }
    }

    screenRemove(index: number) {
        if (this.editActive) {
            this.timelineTemplate().screen_ids.splice(index, 1);
        }
    }

    screenAdd() {
        if (this.editActive && this.addScreenActive && this.selectedScreen) {
            this.timelineTemplate().screen_ids.push(this.selectedScreen);
        }
        this.addScreenActive = false;
    }

    editClose() {
        if (this.editActive) {
            this.editResult.emit(this.timelineTemplate().id);
            this.addScreenActive = false;
            this.editActive = false;
        }
    }

    editActivate() {
        this.createSelectableUsers();
        this.editActive = true;
    }

    addScreenActivate() {
        this.createSelectableScreens();
        this.addScreenActive = true;
    }

    saveTimelineTemplate() {
        if (this.editActive) {
            if (this.timelineTemplate().id)
                this.ttService
                    .updateTimelineTemplate(this.timelineTemplate())
                    .subscribe((result: any) => {
                        next: this.editClose();
                    });
            else
                this.ttService
                    .createTimelineTemplate(this.timelineTemplate())
                    .subscribe((result: any) => {
                        next: {
                            if (Object.keys(result).includes('created'))
                                this.timelineTemplate().id = result['created'];
                            this.editClose();
                        }
                    });
        }
    }

    duplicateTimelineTemplate() {
        let tt: TimelineTemplate = <TimelineTemplate>{'desc': this.timelineTemplate().desc + ' - duplicate', 'user_id': this.currentUser().id, 'screen_ids': this.timelineTemplate().screen_ids};
        this.ttService
            .createTimelineTemplate(tt)
            .subscribe((result: any) => {
                next: {
                    if (Object.keys(result).includes('created')) this.editResult.emit(result['created']);
                }
            });
    }

    deleteTimelineTemplate() {
        if (this.timelineTemplate().id)
            this.ttService
                .deleteTimelineTemplate(this.timelineTemplate().id!)
                .subscribe((result: any) => {
                    next: this.editResult.emit(this.timelineTemplate().id);
                });
    }
}
