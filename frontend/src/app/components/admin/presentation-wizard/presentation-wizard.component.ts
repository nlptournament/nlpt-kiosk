import { Component, input, model, OnInit } from '@angular/core';

import { User } from '../../../interfaces/user';
import { Media, MediaType, MediaSrcType } from '../../../interfaces/media';
import { TimelineTemplate } from '../../../interfaces/timeline-template';

import { MediaService } from '../../../services/media.service';
import { TimelineTemplateService } from '../../../services/timeline-template.service';

import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { FileUploadModule } from 'primeng/fileupload';
import { InputNumberModule } from 'primeng/inputnumber';

interface selectableElement {
    code: string | null;
    name: string;
}

@Component({
  selector: 'presentation-wizard',
  imports: [CommonModule, Dialog, FormsModule, SelectModule, InputTextModule, ButtonModule, FileUploadModule, InputNumberModule],
  templateUrl: './presentation-wizard.component.html',
  styleUrl: './presentation-wizard.component.scss'
})
export class PresentationWizardComponent implements OnInit {
    isActive = model.required<boolean>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    medias =  input.required<Map<string, Media>>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();

    isVisible: boolean = true;
    selectableUsers: selectableElement[] = [];
    selectableMedias: selectableElement[] = [];
    selectableTimelineTemplates: selectableElement[] = [];

    selectedUser: string | null = null;
    selectedMedia: string | null = null;
    selectedMediaFile: File | null = null;
    selectedTimelineTemplate: string | null = null;
    commonDesc: string = "";
    image_width: number = 1920;

    constructor(
        private mediaService: MediaService,
        private timelineTemplateService: TimelineTemplateService
    ) {}

    ngOnInit(): void {
        this.createSelectableUsers();
    }

    userChanged() {
        this.selectedMedia = null;
        this.selectedTimelineTemplate = null;
        this.commonDesc = "";
        if (this.selectedUser != null) {
            this.commonDesc = "Presentation of " + this.users().get(this.selectedUser)!.login;
            this.createSelectableMedia();
            this.createSelectableTimelineTemplates();
        }
    }

    createSelectableUsers() {
        let su: selectableElement[] = [];
        su.push(<selectableElement>{code: null, name: '--select--'});
        if (this.currentUser().admin) {
            for (let k of this.users().keys()) {
                su.push(<selectableElement>{code: k, name: this.users().get(k)!.login});
            }
        }
        else {
            su.push(<selectableElement>{code: this.currentUser().id, name: this.currentUser().login});
        }
        this.selectableUsers = su;
    }

    createSelectableMedia() {
        let sm: selectableElement[] = [];
        sm.push(<selectableElement>{code: null, name: '--upload new--'});
        for (let k of this.medias().keys()) {
            let m: Media = this.medias().get(k)!;
            if (m.user_id == this.selectedUser && m.type == MediaType.other && m.src_type == MediaSrcType['internal S3 storage'])
                sm.push(<selectableElement>{code: k, name: m.desc});
        }
        this.selectableMedias = sm;
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

    mediaFileSelected(event: any) {
        if (event.files.length > 0) {
            this.selectedMediaFile = event.files[0];
        }
        else {
            this.selectedMediaFile = null;
        }
    }

    saveMedia() {
        if (this.selectedMedia) this.saveTimelineTemplate(this.selectedMedia);
        else if (this.selectedMediaFile) {
            let media: Media = <Media>{desc: this.commonDesc + ' PDF', type: MediaType.other, src_type: MediaSrcType['internal S3 storage'], common: false, user_id: this.selectedUser};
            this.mediaService.createMedia(media).subscribe({
                next: (result: any) => {
                    this.uploadMediaFile(result['created']);
                },
                error: () => {}
            });
        }
    }

    uploadMediaFile(media_id: string) {
        if (this.selectedMediaFile) {
            this.mediaService.uploadMediaFile(media_id, this.selectedMediaFile).subscribe({
                next: (result: any) => {
                    this.saveTimelineTemplate(media_id);
                },
                error: () => {}
            });
        }
    }

    saveTimelineTemplate(media_id: string) {
        let tt: TimelineTemplate;
        if (this.selectedTimelineTemplate) {
            tt = this.timelineTemplates().get(this.selectedTimelineTemplate)!;
            tt.presentation = true;
            this.timelineTemplateService.updateTimelineTemplate(tt).subscribe({
                next: (result: any) => {
                    this.importPdf(media_id, this.selectedTimelineTemplate!);
                },
                error: () => {}
            });
        }
        else {
            tt = <TimelineTemplate>{desc: this.commonDesc, user_id: this.selectedUser, presentation: true};
            this.timelineTemplateService.createTimelineTemplate(tt).subscribe({
                next: (result: any) => {
                    this.importPdf(media_id, result['created']);
                },
                error: () => {}
            });
        }
    }

    importPdf(media_id: string, tt_id: string) {
        this.timelineTemplateService.importPdf(tt_id, media_id, this.commonDesc + ' page ', this.image_width).subscribe({
            next: (result: any) => {
                this.closeDialog();
            },
            error: () => {}
        });
    }
}
