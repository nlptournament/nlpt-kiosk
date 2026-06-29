import { Component } from '@angular/core';
import { ErrorHandlerService } from '../../../services/error-handler.service';
import { PresentationService } from '../../../services/presentation.service';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-presenter-screen',
  imports: [CommonModule],
  templateUrl: './presenter-screen.component.html',
  styleUrl: './presenter-screen.component.scss'
})
export class PresenterScreenComponent {

    constructor(
        private errorHandler: ErrorHandlerService,
        private presentationService: PresentationService
    ) { }

    exec_forward() {
        this.presentationService.execForward().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    exec_backward() {
        this.presentationService.execBackward().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    exec_restart() {
        this.presentationService.execRestart().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }
}
