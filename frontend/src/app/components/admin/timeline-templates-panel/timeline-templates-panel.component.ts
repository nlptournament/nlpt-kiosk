import { Component, input, output, model, OnInit } from '@angular/core';

import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { Media } from '../../../interfaces/media';

import { CommonModule } from '@angular/common';
import { TimelineTemplateComponent } from '../../elements/timeline-template/timeline-template.component';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms'
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { TooltipModule } from 'primeng/tooltip';

interface selectableUser {
    code: string | null;
    name: string;
}

@Component({
  selector: 'panel-timeline-templates',
  imports: [CommonModule, TimelineTemplateComponent, Dialog, FormsModule, SelectModule, InputTextModule, TooltipModule],
  templateUrl: './timeline-templates-panel.component.html',
  styleUrl: './timeline-templates-panel.component.scss'
})
export class TimelineTemplatesPanelComponent implements OnInit {
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    medias = input.required<Map<string, Media>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    createTtDummy: TimelineTemplate = <TimelineTemplate>{};
    createTtActive: boolean = false;

    showHiddenTT: boolean = false;
    filterDesc: string = "";
    filterUser: string | null = null;
    filterUserEqual: boolean = true;
    selectableUsers: selectableUser[] = [];

    ngOnInit(): void {
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

    createTt() {
        this.createTtDummy = <TimelineTemplate>{desc: '', user_id: this.currentUser().id, screen_ids: <string[]>[]};
        this.createTtActive = true;
    }

    ttCreated(event: string|null|undefined) {
        this.createTtActive = false;
    }

    closeDialog() {
        this.isActive.set(false);
    }
}
