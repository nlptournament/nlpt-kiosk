import { CommonModule, DecimalPipe } from '@angular/common';
import { Component, input, OnDestroy, OnInit } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { TasService } from '../../../services/tas.service';
import { TasChallengeRank, TasGlobalRank } from '../../../interfaces/tas';

@Component({
  selector: 'screen-tas',
  imports: [CommonModule, DecimalPipe],
  templateUrl: './tas.component.html',
  styleUrl: './tas.component.scss'
})
export class TasComponent implements OnInit, OnDestroy {
    isActive = input.required<boolean>();

    refreshTasTimer = timer(10000, 10000);
    refreshTasTimerSubscription: Subscription | undefined;

    challenge_ranks: TasChallengeRank[] = [];
    global_ranks: TasGlobalRank[] = [];
    c_scale: number = 0;
    g_scale: number = 0;

    constructor(
        private tasService: TasService
    ) {}

    ngOnInit(): void {
        this.refreshTas();
        this.refreshTasTimerSubscription = this.refreshTasTimer.subscribe(() => this.refreshTas());
    }

    ngOnDestroy(): void {
        this.refreshTasTimerSubscription?.unsubscribe();
    }

    refreshTas() {
        this.tasService.getChallengeRanks().subscribe({
            next: (cranks: TasChallengeRank[]) => {
                this.challenge_ranks = cranks;
                if (cranks.length <= 14) this.c_scale = 2;
                else if (cranks.length <= 17) this.c_scale = 1;
                else this.c_scale = 0;
            },
            error: () => {}
        });
        this.tasService.getGlobalRanks().subscribe({
            next: (granks: TasGlobalRank[]) => {
                this.global_ranks = granks;
                if (granks.length <= 14) this.g_scale = 2;
                else if (granks.length <= 17) this.g_scale = 1;
                else this.g_scale = 0;
            },
            error: () => {}
        });
    }
}
