import { Component, input, output, model } from '@angular/core';

import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';

import { CommonModule } from '@angular/common';
import { TimelineTemplateComponent } from '../../elements/timeline-template/timeline-template.component';
import { Dialog } from 'primeng/dialog';

@Component({
  selector: 'panel-timeline-templates',
  imports: [CommonModule, TimelineTemplateComponent, Dialog],
  templateUrl: './timeline-templates-panel.component.html',
  styleUrl: './timeline-templates-panel.component.scss'
})
export class TimelineTemplatesPanelComponent {
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplateEdited = output<string|null|undefined>();
    timelineEdited = output<string|null|undefined>();
    screenEdited = output<string|null|undefined>();
    isActive = model.required<boolean>();

    createTtDummy: TimelineTemplate = <TimelineTemplate>{};
    createTtActive: boolean = false;

    createTt() {
        this.createTtDummy = <TimelineTemplate>{desc: '', user_id: this.currentUser().id, screen_ids: <string[]>[]};
        this.createTtActive = true;
    }

    ttCreated(event: string|null|undefined) {
        this.timelineTemplateEdited.emit(event);
        this.createTtActive = false;
    }
}
