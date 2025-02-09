import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-player-counts',
  imports: [],
  templateUrl: './player-counts.component.html',
  styleUrl: './player-counts.component.scss'
})
export class PlayerCountsComponent implements OnInit {
    counts: any[] = [];

    ngOnInit(): void {
        this.counts.push({'name': 'Server3', 'count': 2, 'game': 'UT2k4'});
        this.counts.push({'name': 'Server2', 'count': 2, 'game': 'UT2k4'});
        this.counts.push({'name': 'Server1', 'count': 2, 'game': 'UT2k4'});
        this.counts.push({'name': 'Server1', 'count': 3, 'game': 'UT3'});
        this.counts.push({'name': 'Server4', 'count': 0, 'game': 'UT3'});
        this.counts.push({'name': 'Server2', 'count': 3, 'game': 'UT3'});
        this.counts.push({'name': 'Server3', 'count': 3, 'game': 'UT3'});
        this.counts.push({'name': 'Server3', 'count': 2, 'game': 'Battlefield2'});
        this.counts.push({'name': 'Server2', 'count': 3, 'game': 'Battlefield2'});
        this.counts.push({'name': 'Server1', 'count': 1, 'game': 'Battlefield2'});
        this.counts.push({'name': 'OpenWorld', 'count': 0, 'game': 'Minecraft'});
        this.counts.push({'name': 'Tournament', 'count': 10, 'game': 'Minecraft'});
        this.counts.push({'name': 'Server1', 'count': 0, 'game': 'CoD4'});
        this.counts.push({'name': 'Server2', 'count': 0, 'game': 'CoD4'});
        this.counts.push({'name': 'Server3', 'count': 0, 'game': 'CoD4'});
        this.counts.push({'name': 'Server1', 'count': 2, 'game': 'CoD2'});
        this.counts.push({'name': 'Server2', 'count': 2, 'game': 'CoD2'});
        this.counts.push({'name': 'Server3', 'count': 2, 'game': 'CoD2'});
        this.counts.push({'name': 'NLPT', 'count': 69, 'game': 'Mordhau'});
        this.counts.push({'name': 'Geheimbasis', 'count': 3, 'game': 'Left4Dead2'});

        this.counts = this.counts.sort((a, b) => (a.game > b.game ? 1 : (a.game < b.game ? -1 : (a.name > b.name ? 1 : (a.name < b.name ? -1 : 0)))));
    }
}
