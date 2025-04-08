import { CommonModule } from '@angular/common';
import { Component, input, OnInit, output } from '@angular/core';
import { Subscription, timer } from 'rxjs';

@Component({
  selector: 'screen-timer',
  imports: [CommonModule],
  templateUrl: './timer.component.html',
  styleUrl: './timer.component.scss'
})
export class TimerComponent implements OnInit {
    isActive = input.required<boolean>();
    finished = output<null>();

    refreshCountdownTimer = timer(1000, 1000);
    refreshCountdownTimerSubscription: Subscription | undefined;

    countdown: string = '00:00:00';
    target: number = 0;
    title: string | undefined | null = "Ein Titel";
    subtitle: string | undefined | null = "Eine Unterschrift";

    ngOnInit(): void {
        if (this.target == 0) {
            //this.target = Date.now() / 1000 + 3615;
            this.target = Date.now() / 1000 + 72;
            this.updateCountdown();
            this.refreshCountdownTimerSubscription = this.refreshCountdownTimer.subscribe(() => this.updateCountdown());
        }
    }

    updateCountdown() {
        let diff: number = this.target - Date.now() / 1000;
        if (diff <= 0) {
            this.finished.emit(null);
            this.countdown = '00:00:00';
            this.refreshCountdownTimerSubscription?.unsubscribe();
        }
        else {
            let h: number = Math.floor(diff / 3600);
            diff = diff % 3600;
            let m: number = Math.floor(diff / 60);
            let s: number = Math.floor(diff % 60);
            this.countdown = (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
        }
    }
}
