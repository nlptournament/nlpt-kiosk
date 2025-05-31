import { Component, input, OnInit, output } from '@angular/core';

import { Media, MediaSrcType, MediaType } from '../../../interfaces/media';
import { User } from '../../../interfaces/user';

import { MediaService } from '../../../services/media.service';

import { CommonModule } from '@angular/common';
import { TooltipModule } from 'primeng/tooltip';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { IftaLabelModule } from 'primeng/iftalabel';
import { ButtonModule } from 'primeng/button';
import { SelectModule } from 'primeng/select';
import { SelectButtonModule } from 'primeng/selectbutton';
import { FileUploadModule } from 'primeng/fileupload';

interface selectableCommon {
    code: boolean,
    name: string
}

interface selectableUser {
    code: string;
    name: string;
}

interface selectableType {
    code: number;
    name: string;
}

@Component({
  selector: 'element-media',
  imports: [CommonModule, Dialog, FormsModule, InputTextModule, IftaLabelModule, ButtonModule, SelectModule, SelectButtonModule, FileUploadModule, TooltipModule],
  templateUrl: './media.component.html',
  styleUrl: './media.component.scss'
})
export class MediaComponent implements OnInit {
    media =  input.required<Media>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    editResult = output<string|null|undefined>();

    mediaSrcType = MediaSrcType;
    mediaType = MediaType;

    selectedFile: File | undefined;
    editActive: boolean = false;
    selectableCommons: selectableCommon[] = [];
    selectableUsers: selectableUser[] = [];
    selectableSrcTypes: selectableType[] = [];
    selectableTypes: selectableType[] = [];

    constructor(
        private mediaService: MediaService
    ) {}

    ngOnInit(): void {
        this.selectableCommons.push(<selectableCommon>{code: true, 'name': 'available2everyone'});
        this.selectableCommons.push(<selectableCommon>{code: false, 'name': 'just4owner'});
        this.createSelectableUsers();
        this.createSelectableTypes();
    }

    createSelectableTypes() {
        let st: selectableType[] = [];
        let vt = Object.values(this.mediaType);
        for (let i = 0; i < vt.length / 2; i++) {
            st.push(<selectableType>{code: i, name: vt[i]});
        }
        this.selectableTypes = st;
        st = [];
        let vst = Object.values(this.mediaSrcType);
        for (let i = 0; i < vst.length / 2; i++) {
            st.push(<selectableType>{code: i, name: vst[i]});
        }
        this.selectableSrcTypes = st;
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login})
        }
        this.selectableUsers = su;
    }

    editClose() {
        if (this.editActive) {
            this.editActive = false;
            this.editResult.emit(this.media().id);
        }
    }

    mediaFileSelected(event: any) {
        if (event.files.length > 0) {
            this.selectedFile = event.files[0];
        }
        else {
            this.selectedFile = undefined;
        }
    }

    saveMedia() {
        if (this.editActive) {
            if (this.media().id) {
                this.mediaService
                    .updateMedia(this.media())
                    .subscribe({
                        next: (result: any) => {
                            this.uploadMediaFile();
                        }
                    });
            }
            else {
                this.mediaService
                    .createMedia(this.media())
                    .subscribe({
                        next: (result: Media) => {
                            this.media().id = result.id;
                            this.uploadMediaFile();
                        }
                    });
            }
        }
        this.mediaService
            .updateMedia(this.media())
    }

    uploadMediaFile() {
        if (this.selectedFile) {
            this.mediaService
                .uploadMediaFile(this.media().id, this.selectedFile)
                .subscribe({
                    next: (result: any) => {
                        this.editClose();
                    }
                });
        }
        else this.editClose();
    }

    deleteMedia() {}

}
