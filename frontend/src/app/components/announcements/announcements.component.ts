import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-announcements',
  imports: [CommonModule],
  templateUrl: './announcements.component.html',
  styleUrl: './announcements.component.scss'
})
export class AnnouncementsComponent implements OnInit {
    announce: any[] =[];

    ngOnInit(): void {
        this.announce.push({'layout': 'default', 'title': 'Test', 'msg': 'Eine Nachricht', 'time': 'jetzt', 'img': ''});
        this.announce.push({'layout': 'danger', 'title': 'Pommes fassen', 'msg': 'Ein Flasche Pommes bitte', 'time': '00:23:45', 'img': ''});
        this.announce.push({'layout': 'ffa', 'title': 'Fall Guys', 'msg': 'Alle zusammen um 02:00 Uhr.', 'time': '01:23:45', 'img': 'FallGuys.jpg'});
        this.announce.push({'layout': 'default', 'title': 'Heizung aus', 'msg': 'Eis für alle, Eis für alle. Oder geht einfach schlafen!', 'time': '02:23:45', 'img': ''});
    }
}
