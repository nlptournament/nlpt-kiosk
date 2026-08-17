import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';

import { ScreenService } from '../../../services/screen.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';

import { Screen } from '../../../interfaces/screen';
import { StreamPlayerComponent } from '../../screens/stream-player/stream-player.component';

@Component({
  selector: 'participant-stream-viewer',
  imports: [RouterModule, StreamPlayerComponent],
  templateUrl: './stream-viewer.component.html',
  styleUrl: './stream-viewer.component.scss'
})
export class StreamViewerComponent implements OnInit {
    screen?: Screen;
    notFound = false;

    constructor(
        private route: ActivatedRoute,
        private errorHandler: ErrorHandlerService,
        private screenService: ScreenService
    ) {}

    ngOnInit(): void {
        const screenId = this.route.snapshot.paramMap.get('screenId');
        if (!screenId) {
            this.notFound = true;
            return;
        }
        this.screenService.getScreen(screenId).subscribe({
            next: (screen: Screen) => {
                this.screen = screen;
            },
            error: (err: HttpErrorResponse) => {
                if (err.status === 404 || err.status === 400) {
                    this.notFound = true;
                } else {
                    this.errorHandler.handleError(err);
                    this.notFound = true;
                }
            }
        });
    }

}
