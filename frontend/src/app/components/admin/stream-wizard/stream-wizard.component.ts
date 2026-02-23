import { Component, input, model, OnInit } from '@angular/core';

import { User } from '../../../interfaces/user';
import { Media, MediaType, MediaSrcType } from '../../../interfaces/media';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { TimelineTemplate } from '../../../interfaces/timeline-template';

import { ScreenService } from '../../../services/screen.service';
import { MediaService } from '../../../services/media.service';
import { TimelineTemplateService } from '../../../services/timeline-template.service';

import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';


interface selectableElement {
    code: string | null;
    name: string;
}

@Component({
  selector: 'stream-wizard',
  imports: [CommonModule, Dialog, FormsModule, SelectModule, InputTextModule, ButtonModule],
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

    streamScreenTemplate: string | null = null;
    selectedUser: string | null = null;
    selectedMedia: string | null = null;
    selectedScreen: string | null = null;
    selectedTimelineTemplate: string | null = null;
    streamUrl: string = "";
    commonDesc: string = "";

    constructor(
        private screenService: ScreenService,
        private mediaService: MediaService,
        private timelineTemplateService: TimelineTemplateService
    ) {}

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
        if (!this.streamScreenTemplate) {
            for (let k of this.screenTemplates().keys()) {
                let st: ScreenTemplate = this.screenTemplates().get(k)!;
                if (st.name == 'Stream') {
                    this.streamScreenTemplate = st.id;
                    break;
                }
            }
        }
        if (this.streamScreenTemplate) {
            ss.push(<selectableElement>{code: null, name: '--create new--'});
            for (let k of this.screens().keys()) {
                let s: Screen = this.screens().get(k)!;
                if (s.template_id == this.streamScreenTemplate && s.user_id == this.selectedUser)
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

    saveMedia() {
        if (!this.streamScreenTemplate) return;

        let media: Media;
        if (this.selectedMedia) {
            media = this.medias().get(this.selectedMedia)!;
            media.common = false;
            this.mediaService.updateMedia(media).subscribe({
                next: (result: any) => {
                    this.saveScreen(result['updated']);
                },
                error: () => {}
            });
        }
        else {
            media = <Media>{desc: this.commonDesc, type: MediaType.stream, src_type: MediaSrcType['generic web URL'], src: this.streamUrl, common: false, user_id: this.selectedUser};
            this.mediaService.createMedia(media).subscribe({
                next: (result: any) => {
                    this.saveScreen(result['created']);
                },
                error: () => {}
            });
        }
    }

    saveScreen(media_id: string) {
        if (!this.streamScreenTemplate) return;
        let screenTemplate: ScreenTemplate = this.screenTemplates().get(this.streamScreenTemplate)!;
        let screen: Screen;
        if (this.selectedScreen) {
            screen = this.screens().get(this.selectedScreen)!;
            screen.variables = {stream: media_id};
            this.screenService.updateScreen(screen).subscribe({
                next: (result: any) => {
                    this.saveTimelineTemplate(result["updated"]);
                },
                error: () => {}
            });
        }
        else {
            screen = <Screen>{desc: this.commonDesc, key: screenTemplate.key, template_id: screenTemplate.id, user_id: this.selectedUser, variables: {stream: media_id}};
            this.screenService.createScreen(screen).subscribe({
                next: (result: any) => {
                    this.saveTimelineTemplate(result["created"]);
                },
                error: () => {}
            });
        }
    }

    saveTimelineTemplate(screen_id: string) {
        let template: TimelineTemplate;
        if (this.selectedTimelineTemplate) {
            template = this.timelineTemplates().get(this.selectedTimelineTemplate)!;
            template.screen_ids = [screen_id];
            this.timelineTemplateService.updateTimelineTemplate(template).subscribe({
                next: (result: any) => {
                    this.closeDialog();
                },
                error: () => {}
            });
        }
        else {
            template = <TimelineTemplate>{desc: this.commonDesc, user_id: this.selectedUser, screen_ids: [screen_id]};
            this.timelineTemplateService.createTimelineTemplate(template).subscribe({
                next: (result: any) => {
                    this.closeDialog();
                },
                error: () => {}
            });
        }
    }
}
