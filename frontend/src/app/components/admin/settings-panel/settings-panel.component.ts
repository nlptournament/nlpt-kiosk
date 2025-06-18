import { Component, model, OnInit } from '@angular/core';
import { SettingService } from '../../../services/setting.service';
import { Setting } from '../../../interfaces/setting';
import { HttpErrorResponse } from '@angular/common/http';
import { ErrorHandlerService } from '../../../services/error-handler.service';
import { Dialog } from 'primeng/dialog';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { InputNumberModule } from 'primeng/inputnumber';

const anno_uri_default = "https://dev.nlpt.online/api/announcements?token=";

@Component({
  selector: 'panel-settings',
  imports: [CommonModule, Dialog, FormsModule, InputTextModule, ButtonModule, InputNumberModule],
  templateUrl: './settings-panel.component.html',
  styleUrl: './settings-panel.component.scss'
})
export class SettingsPanelComponent implements OnInit {
    isActive = model.required<boolean>();
    isVisible: boolean = true;
    settings: Setting[] = [];

    constructor(
        private settingService: SettingService,
        private errorHandler: ErrorHandlerService
    ) {}

    ngOnInit(): void {
        this.refreshSettings();
    }

    refreshSettings() {
        this.settingService
            .getSettings().subscribe({
                next: (settings: Setting[]) => {
                    for (let setting of settings) {
                        if (setting.id == 'anno_src_uri' && (!setting.value || setting.value == '')) setting.value = anno_uri_default;
                    }
                    this.settings = settings.sort((a, b) => (a.id > b.id) ? 1 : ((a.id < b.id) ? -1 : 0));
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    saveSettings() {
        for (let setting of this.settings) {
            if (!setting.ro) {
                this.settingService
                    .updateSetting(setting).subscribe({
                        next: () => {
                            if (setting.id == this.settings[this.settings.length - 1].id) this.closeDialog();
                        },
                        error: () => {}
                    });
            }
        }
    }

    closeDialog() {
        this.isActive.set(false);
    }
}
