import { Component, model, OnInit } from '@angular/core';
import { GameAbbr } from '../../../interfaces/game-abbr';

import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { GameAbbrComponent } from '../../elements/game-abbr/game-abbr.component';
import { GameAbbrService } from '../../../services/game-abbr.service';

@Component({
  selector: 'panel-game-abbr',
  imports: [CommonModule, Dialog, GameAbbrComponent],
  templateUrl: './game-abbr-panel.component.html',
  styleUrl: './game-abbr-panel.component.scss'
})
export class GameAbbrPanelComponent implements OnInit {
    isActive = model.required<boolean>();

    gameAbbrs: GameAbbr[] = [];
    isVisible: boolean = true;
    dummyGameAbbr: GameAbbr | undefined = undefined;

    constructor(
        private gameAbbrService: GameAbbrService
    ) { }

    ngOnInit() {
        this.refreshGameAbbrs();
    }

    refreshGameAbbrs() {
        this.gameAbbrService.getGameAbbrs().subscribe({
            next: (gameAbbrs: GameAbbr[]) => {
                this.gameAbbrs = gameAbbrs;
            }
        });
    }

    closeDialog() {
        this.isActive.set(false);
    }

    createGameAbbr() {
        this.dummyGameAbbr = <GameAbbr>{enabled: true};
    }

    updatedGameAbbr() {
        this.refreshGameAbbrs();
        this.dummyGameAbbr = undefined;
    }
}
