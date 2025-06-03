import { booleanAttribute, Component, input, output } from '@angular/core';
import { Timeline } from '../../../interfaces/timeline';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { ScreenComponent } from '../screen/screen.component';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { Media } from '../../../interfaces/media';
import { CommonModule } from '@angular/common';
import { SliderModule } from 'primeng/slider';
import { FormsModule } from '@angular/forms';
import { TimelineService } from '../../../services/timeline.service';
import { TooltipModule } from 'primeng/tooltip';

@Component({
  selector: 'element-timeline',
  imports: [CommonModule, FormsModule, SliderModule, ScreenComponent, TooltipModule],
  templateUrl: './timeline.component.html',
  styleUrl: './timeline.component.scss'
})
export class TimelineComponent {
    timeline = input.required<Timeline>();
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    medias = input.required<Map<string, Media>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    roMode = input(false, {transform: booleanAttribute});
    editResult = output<string|null|undefined>();

    editActive: boolean = false;

    constructor(
        private timelineService: TimelineService
    ) { }

    editClose() {
        this.editResult.emit(this.timeline().id);
        this.editActive = false;
    }

    timelineSave() {
        this.timelineService
            .updateTimeline(this.timeline())
            .subscribe({
                next: (result: any) => {
                    this.editResult.emit(this.timeline().id);
                }
            });
        this.editActive = false;
    }

    timelineDelete() {
        if (this.timeline().id)
            this.timelineService
                .deleteTimeline(this.timeline().id!)
                .subscribe({
                    next: (result: any) => {
                        this.editResult.emit(this.timeline().id);
                    }
                });
    }
}
