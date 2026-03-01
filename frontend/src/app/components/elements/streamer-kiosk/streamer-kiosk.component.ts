import { Component, input } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';

import { Kiosk } from '../../../interfaces/kiosk';
import { User } from '../../../interfaces/user';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { Timeline } from '../../../interfaces/timeline';

import { KioskService } from '../../../services/kiosk.service';

import { CommonModule } from '@angular/common';
import { TooltipModule } from 'primeng/tooltip';
import { ErrorHandlerService } from '../../../services/error-handler.service';

@Component({
  selector: 'element-streamer-kiosk',
  imports: [CommonModule, TooltipModule],
  templateUrl: './streamer-kiosk.component.html',
  styleUrl: './streamer-kiosk.component.scss'
})
export class StreamerKioskComponent {
    kiosk = input.required<Kiosk>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    timelines = input.required<Map<string, Timeline>>();
    ownStreamTTids = input.required<string[]>();
    otherStreamTTids = input.required<string[]>();
    selectedTTid = input.required<string | undefined>();

    constructor(
        private kioskService: KioskService,
        private errorHandler: ErrorHandlerService
    ) {}

    startStream() {
        if (this.selectedTTid()) {
            this.kioskService.applyTimelineTemplate(this.kiosk().id, this.selectedTTid()!).subscribe({
                next: () => {},
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
        }
    }

    stopStream() {
        this.kioskService.applyDefault(this.kiosk().id).subscribe({
            next: () => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }
}
