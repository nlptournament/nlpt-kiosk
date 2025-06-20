import { CommonModule } from '@angular/common';
import { Component, input, OnDestroy, OnInit } from '@angular/core';
import { PlayercountService } from '../../../services/playercount.service';
import { Subscription, timer } from 'rxjs';
import { Playercount } from '../../../interfaces/playercount';

@Component({
  selector: 'screen-player-counts',
  imports: [CommonModule],
  templateUrl: './player-counts.component.html',
  styleUrl: './player-counts.component.scss'
})
export class PlayerCountsComponent implements OnInit, OnDestroy {
    isActive = input.required<boolean>();

    refreshPlayercountsTimer = timer(10000, 10000);
    refreshPlayercountsTimerSubscription: Subscription | undefined;

    counts: any[] = [];

    constructor(
      private playercountService: PlayercountService
    ) {}

    ngOnInit(): void {
        this.refreshPlayercounts();
        this.refreshPlayercountsTimerSubscription = this.refreshPlayercountsTimer.subscribe(() => this.refreshPlayercounts());
    }

    ngOnDestroy(): void {
        this.refreshPlayercountsTimerSubscription?.unsubscribe();
    }

    refreshPlayercounts() {
      this.playercountService
          .getPlayercounts().subscribe({
              next: (playercounts: Playercount[]) => {
                  this.counts = playercounts;
              },
              error: () => {}
          });
    }
}
