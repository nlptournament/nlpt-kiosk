import { Component } from '@angular/core';

@Component({
  selector: 'app-timer',
  imports: [],
  templateUrl: './timer.component.html',
  styleUrl: './timer.component.scss'
})
export class TimerComponent {
    countdown_h: number | string = '01';
    countdown_m: number | string = 16;
    countdown_s: number | string = '04';
    title: string | undefined | null = "Ein Titel";
    subtitle: string | undefined | null = "Eine Unterschrift";
}
