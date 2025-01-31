import { DecimalPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-tas',
  imports: [DecimalPipe],
  templateUrl: './tas.component.html',
  styleUrl: './tas.component.scss'
})
export class TasComponent implements OnInit {
    challenge_ranks: any[] = [];
    global_ranks: any[] = [];

    ngOnInit(): void {
        this.challenge_ranks.push({'rank': 1, 'player': 'PlayerName1', 'time': 123456});
        this.challenge_ranks.push({'rank': 2, 'player': 'PlayerName2', 'time': 124567});
        this.challenge_ranks.push({'rank': 3, 'player': 'ALongPlayerName', 'time': 124567});
        this.challenge_ranks.push({'rank': 4, 'player': 'AReallyLongPlayerName', 'time': 124567});
        this.challenge_ranks.push({'rank': 6, 'player': 'PlayerName3', 'time': undefined});
        this.challenge_ranks.push({'rank': 6, 'player': 'PlayerName4', 'time': null});

        this.global_ranks.push({'rank': 1, 'player': 'PlayerName1', 'points': 16});
        this.global_ranks.push({'rank': 2, 'player': 'PlayerName2', 'points': 15});
        this.global_ranks.push({'rank': 3, 'player': 'ALongPlayerName', 'points': 14});
        this.global_ranks.push({'rank': 4, 'player': 'AReallyLongPlayerName', 'points': 13});
        this.global_ranks.push({'rank': 5, 'player': 'PlayerName5', 'points': 12});
        this.global_ranks.push({'rank': 6, 'player': 'PlayerName6', 'points': 11});
        this.global_ranks.push({'rank': 7, 'player': 'PlayerName7', 'points': 10});
        this.global_ranks.push({'rank': 8, 'player': 'PlayerName8', 'points': 9});
        this.global_ranks.push({'rank': 9, 'player': 'PlayerName9', 'points': 8});
        this.global_ranks.push({'rank': 10, 'player': 'PlayerName10', 'points': 7});
        this.global_ranks.push({'rank': 11, 'player': 'PlayerName11', 'points': 6});
        this.global_ranks.push({'rank': 12, 'player': 'PlayerName12', 'points': 5});
        this.global_ranks.push({'rank': 13, 'player': 'PlayerName13', 'points': 4});
        this.global_ranks.push({'rank': 14, 'player': 'PlayerName14', 'points': 3});
        this.global_ranks.push({'rank': 15, 'player': 'PlayerName15', 'points': 2});
        this.global_ranks.push({'rank': 17, 'player': 'PlayerName3', 'points': 0});
        this.global_ranks.push({'rank': 17, 'player': 'PlayerName4', 'points': 0});
    }
}
