import { booleanAttribute, Component, input, OnInit, output } from '@angular/core';
import { GameAbbr } from '../../../interfaces/game-abbr';
import { GameAbbrService } from '../../../services/game-abbr.service';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { Checkbox } from 'primeng/checkbox';
import { TooltipModule } from 'primeng/tooltip';

@Component({
  selector: 'element-game-abbr',
  imports: [CommonModule, FormsModule, InputTextModule, Checkbox, TooltipModule],
  templateUrl: './game-abbr.component.html',
  styleUrl: './game-abbr.component.scss'
})
export class GameAbbrComponent implements OnInit {
  gameAbbr = input.required<GameAbbr>();
  editMode = input(false, {transform: booleanAttribute});
  editResult = output<string|null|undefined>();

  editActive: boolean = false;

  constructor(
      private gameAbbrService: GameAbbrService
  ) { }

  ngOnInit(): void {
      this.editActive = this.editMode();
  }

  editClose() {
      this.editResult.emit(this.gameAbbr().id);
      this.editActive = false;
  }

  saveGameAbbr() {
      if (this.gameAbbr().id) {
          this.gameAbbrService.updateGameAbbr(this.gameAbbr()).subscribe((result: any) => {
              next: this.editClose();
          });
      }
      else {
        this.gameAbbrService.createGameAbbr(this.gameAbbr()).subscribe((result: any) => {
            next: this.editClose();
        });
      }
  }

  deleteGameAbbr() {
    if (this.gameAbbr().id) {
        this.gameAbbrService.deleteGameAbbr(this.gameAbbr().id).subscribe((result: any) => {
            next: this.editClose();
        });
    }
  }

}
