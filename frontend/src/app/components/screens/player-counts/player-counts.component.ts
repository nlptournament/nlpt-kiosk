import { CommonModule } from '@angular/common';
import { Component, input, OnDestroy, OnInit } from '@angular/core';
import { PlayercountService } from '../../../services/playercount.service';
import { Subscription, timer } from 'rxjs';
import { Playercount, PlayercountDiscord } from '../../../interfaces/playercount';

@Component({
  selector: 'screen-player-counts',
  imports: [CommonModule],
  templateUrl: './player-counts.component.html',
  styleUrl: './player-counts.component.scss'
})
export class PlayerCountsComponent implements OnInit, OnDestroy {
    isActive = input.required<boolean>();
    variables = input.required<any>();

    refreshPlayercountsPrometheusTimer = timer(8000, 8000);
    refreshPlayercountsPrometheusTimerSubscription: Subscription | undefined;
    refreshPlayercountsDiscordTimer = timer(3000, 3000);
    refreshPlayercountsDiscordTimerSubscription: Subscription | undefined;


    src_prometheus: boolean = false;
    src_discord: boolean = false;
    discord_guild_id: string | undefined = undefined;
    discord_role_id: string | undefined = undefined;

    counts_prometheus: Playercount[] = [];
    counts_discord: PlayercountDiscord[] = [];
    scale: number = 0;
    scale_discord: number = 0;
    scale_w_discord: number = 23;

    constructor(
      private playercountService: PlayercountService
    ) {}

    ngOnInit(): void {
        if (Object.keys(this.variables()).includes('src_prom')) this.src_prometheus = this.variables()['src_prom'];
        if (Object.keys(this.variables()).includes('src_discord')) this.src_discord = this.variables()['src_discord'];
        if (Object.keys(this.variables()).includes('guild')) this.discord_guild_id = this.variables()['guild'];
        if (Object.keys(this.variables()).includes('role')) this.discord_role_id = this.variables()['role'];
        if (this.src_prometheus) {
            this.refreshPlayercountsPrometheus();
            this.refreshPlayercountsPrometheusTimerSubscription = this.refreshPlayercountsPrometheusTimer.subscribe(() => this.refreshPlayercountsPrometheus());
        }
        if (this.src_discord) {
            this.refreshPlayercountsDiscord();
            this.refreshPlayercountsDiscordTimerSubscription = this.refreshPlayercountsDiscordTimer.subscribe(() => this.refreshPlayercountsDiscord());
        }
    }

    ngOnDestroy(): void {
        this.refreshPlayercountsPrometheusTimerSubscription?.unsubscribe();
        this.refreshPlayercountsDiscordTimerSubscription?.unsubscribe();
    }

    refreshPlayercountsPrometheus() {
      this.playercountService
          .getPlayercountsPrometheus().subscribe({
              next: (playercounts: Playercount[]) => {
                  this.counts_prometheus = playercounts;
                  if (playercounts.length <= 4) this.scale = 4;
                  else if (playercounts.length <= 9) this.scale = 3;
                  else if (playercounts.length <= 12) this.scale = 2;
                  else if (playercounts.length <= 20) this.scale = 1;
                  else this.scale = 0;
              },
              error: () => {}
          });
    }

    refreshPlayercountsDiscord() {
      this.playercountService
        .getPlayercountsDiscord(this.discord_guild_id, this.discord_role_id).subscribe({
            next: (playercounts: PlayercountDiscord[]) => {
                this.counts_discord = playercounts.sort((a, b) => (
                    (a.count == b.count) ? a.game.localeCompare(b.game) : ((a.count > b.count) ? -1 : 1)
                ));
                if (playercounts.length <= 4) {        // max 4: 90% 9xl und 12xml
                    this.scale_discord = 3;
                    this.scale_w_discord = 90;
                }
                else if (playercounts.length <= 8) {   // max 8: 45% 8xl und 11xml
                    this.scale_discord = 2;
                    this.scale_w_discord = 45;
                }
                else if (playercounts.length <= 15) {  // max 15: 30% 7xl und 10xml
                    this.scale_discord = 1;
                    this.scale_w_discord = 30;
                }
                else {                                 // max 28: 23% 6xl und 9xml
                    this.scale_discord = 0;
                    this.scale_w_discord = 23;
                }
            },
            error: () => {}
        });
    }
}
