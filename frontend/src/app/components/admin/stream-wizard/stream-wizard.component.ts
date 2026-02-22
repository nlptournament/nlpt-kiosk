import { Component, input, model, OnInit } from '@angular/core';

import { User } from '../../../interfaces/user';
import { Media, MediaType } from '../../../interfaces/media';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { TimelineTemplate } from '../../../interfaces/timeline-template';

import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';


interface selectableElement {
    code: string | null;
    name: string;
}

@Component({
  selector: 'stream-wizard',
  imports: [CommonModule, Dialog, FormsModule, SelectModule, InputTextModule],
  templateUrl: './stream-wizard.component.html',
  styleUrl: './stream-wizard.component.scss'
})
export class StreamWizardComponent implements OnInit {
    isActive = model.required<boolean>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    medias =  input.required<Map<string, Media>>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();

    isVisible: boolean = true;
    selectableUsers: selectableElement[] = [];
    selectableMedias: selectableElement[] = [];
    selectableScreens: selectableElement[] = [];
    selectableTimelineTemplates: selectableElement[] = [];

    selectedUser: string | null = null;
    selectedMedia: string | null = null;
    selectedScreen: string | null = null;
    selectedTimelineTemplate: string | null = null;
    streamUrl: string = "";
    commonDesc: string = "";

    ngOnInit(): void {
        this.createSelectableUsers();
    }

    userChanged() {
        this.selectedMedia = null;
        this.streamUrl = "";
        this.selectedScreen = null;
        this.selectedTimelineTemplate = null;
        this.commonDesc = "";
        if (this.selectedUser != null) {
            this.commonDesc = "Stream of " + this.users().get(this.selectedUser)!.login;
            this.createSelectableMedia();
            this.createSelectableScreens();
            this.createSelectableTimelineTemplates();
        }
    }

    createSelectableUsers() {
        let su: selectableElement[] = [];
        su.push(<selectableElement>{code: null, name: '--select--'});
        for (let k of this.users().keys()) {
            su.push(<selectableElement>{code: k, name: this.users().get(k)!.login});
        }
        this.selectableUsers = su;
    }

    createSelectableMedia() {
        let sm: selectableElement[] = [];
        sm.push(<selectableElement>{code: null, name: '--create new--'});
        for (let k of this.medias().keys()) {
            let m: Media = this.medias().get(k)!;
            if (m.user_id == this.selectedUser && m.type == MediaType.stream)
                sm.push(<selectableElement>{code: k, name: m.desc});
        }
        this.selectableMedias = sm;
    }

    createSelectableScreens() {
        let ss: selectableElement[] = [];
        let st_id: string | null = null;
        for (let k of this.screenTemplates().keys()) {
            let st: ScreenTemplate = this.screenTemplates().get(k)!;
            if (st.name == 'Stream') {
                st_id = st.id;
                break;
            }
        }
        if (st_id) {
            ss.push(<selectableElement>{code: null, name: '--create new--'});
            for (let k of this.screens().keys()) {
                let s: Screen = this.screens().get(k)!;
                if (s.template_id == st_id && s.user_id == this.selectedUser)
                    ss.push(<selectableElement>{code: k, name: s.desc});
            }
        }
        this.selectableScreens = ss;
    }

    createSelectableTimelineTemplates() {
        let stt: selectableElement[] = [];
        stt.push(<selectableElement>{code: null, name: '--create new--'});
        for (let k of this.timelineTemplates().keys()) {
            let tt: TimelineTemplate = this.timelineTemplates().get(k)!;
            if (tt.user_id == this.selectedUser)
                stt.push(<selectableElement>{code: k, name: tt.desc});
        }
        this.selectableTimelineTemplates = stt;
    }

    closeDialog() {
        this.isActive.set(false);
    }
}
