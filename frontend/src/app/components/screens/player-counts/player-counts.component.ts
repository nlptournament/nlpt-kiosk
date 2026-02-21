import { CommonModule } from '@angular/common';
import { Component, input, OnDestroy, OnInit } from '@angular/core';
import { PlayercountService } from '../../../services/playercount.service';
import { Subscription, timer } from 'rxjs';
import { PlayercountPrometheus, PlayercountDiscord } from '../../../interfaces/playercount';

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

    counts_prometheus: PlayercountPrometheus[] = [];
    counts_discord: PlayercountDiscord[] = [];
    scale_prometheus: number = 0;
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
              next: (playercounts: PlayercountPrometheus[]) => {
                  if (this.src_discord) {  // in case both sources are active
                    let cpl: PlayercountPrometheus[] = [];
                    // limit the amount of items to 12, with the most active items as priority
                    for (let pc of playercounts.sort((a, b) => (a.count > b.count ? -1 : 1))) {
                        cpl.push(pc);
                        if (cpl.length >= 12) break;
                    }
                    // scale the size to consume as little space as possible
                    if (cpl.length <= 4) this.scale_prometheus = 2;
                    else if (cpl.length <= 5) this.scale_prometheus = 1;
                    else this.scale_prometheus = 0;
                    // sort items by game-name then by server-name
                    this.counts_prometheus = cpl.sort((a, b) => ((a.game.localeCompare(b.game) == 0) ? a.name.localeCompare(b.name) : a.game.localeCompare(b.game)));
                  }
                  else {  // in case only prometheus source is active
                    // scale the size to fit the screen apropriate
                    if (playercounts.length <= 4) this.scale_prometheus = 4;
                    else if (playercounts.length <= 9) this.scale_prometheus = 3;
                    else if (playercounts.length <= 12) this.scale_prometheus = 2;
                    else if (playercounts.length <= 20) this.scale_prometheus = 1;
                    else this.scale_prometheus = 0;
                    // sort items by game-name then by server-name
                    this.counts_prometheus = playercounts.sort((a, b) => ((a.game.localeCompare(b.game) == 0) ? a.name.localeCompare(b.name) : a.game.localeCompare(b.game)));
                  }
              },
              error: () => {}
          });
    }

    refreshPlayercountsDiscord() {
      this.playercountService
        .getPlayercountsDiscord(this.discord_guild_id, this.discord_role_id).subscribe({
            next: (playercounts: PlayercountDiscord[]) => {
                // in case both sources are active handle the scaling, as there would be the double of items
                let pc_len: number = (this.src_prometheus ? playercounts.length * 2: playercounts.length);
                if (pc_len <= 4) {            // max 4: 90% 9xl und 12xml
                    this.scale_discord = 3;
                    this.scale_w_discord = 90;
                }
                else if (pc_len <= 8) {       // max 8: 45% 8xl und 11xml
                    this.scale_discord = 2;
                    this.scale_w_discord = 45;
                }
                else if (pc_len <= 15) {      // max 15: 30% 7xl und 10xml
                    this.scale_discord = 1;
                    this.scale_w_discord = 30;
                }
                else {                        // max 28: 23% 6xl und 9xml
                    this.scale_discord = 0;
                    this.scale_w_discord = 23;
                }
                // sort games by the most player-activity
                this.counts_discord = playercounts.sort((a, b) => (
                    (a.count == b.count) ? a.game.localeCompare(b.game) : ((a.count > b.count) ? -1 : 1)
                ));
            },
            error: () => {}
        });
    }
}
