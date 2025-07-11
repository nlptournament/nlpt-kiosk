import { Component, input, OnDestroy, OnInit, output } from '@angular/core';
import { ChallongeTournamentService } from '../../../services/challonge-tournament.service';
import { ChallongeMatchService } from '../../../services/challonge-match.service';
import { ChallongeParticipantService } from '../../../services/challonge-participant.service';
import { MediaService } from '../../../services/media.service';
import { ChallongeTournament } from '../../../interfaces/challonge-tournament';
import { ChallongeMatch } from '../../../interfaces/challonge-match';
import { ChallongeParticipant } from '../../../interfaces/challonge-participant';
import { Media } from '../../../interfaces/media';
import { CommonModule } from '@angular/common';
import { WebSocketService } from '../../../services/web-socket.service';
import { Subscription } from 'rxjs';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faBoltLightning } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'screen-challonge-round-completion',
  imports: [CommonModule, FontAwesomeModule],
  templateUrl: './challonge-round-completion.component.html',
  styleUrl: './challonge-round-completion.component.scss'
})
export class ChallongeRoundCompletionComponent implements OnInit, OnDestroy {
    faBoltLightning = faBoltLightning;
    isActive = input.required<boolean>();
    variables = input.required<any>();
    finished = output<null>();

    wssSubscription: Subscription | undefined;
    tournament!: ChallongeTournament;
    matches: Map<string, ChallongeMatch> = new Map<string, ChallongeMatch>;
    participants: Map<string, ChallongeParticipant> = new Map<string, ChallongeParticipant>;
    mediaURLs: Map<string, string> = new Map<string, string>;

    tournament_id: string = '';
    title: string = '';
    signal_completed: boolean = false;
    round: number | undefined;
    round_loser: number | undefined;

    constructor(
        private websocketService: WebSocketService,
        private tournamentService: ChallongeTournamentService,
        private matchService: ChallongeMatchService,
        private participantService: ChallongeParticipantService,
        private mediaService: MediaService
    ) {}

    ngOnInit() {
        if (Object.keys(this.variables()).includes('tournament_id')) this.load_tournament(this.variables()['tournament_id']);
        if (Object.keys(this.variables()).includes('title') && this.variables()['title'] != '') this.title = this.variables()['title'];
        if (Object.keys(this.variables()).includes('signal_completed')) this.signal_completed = this.variables()['signal_completed'];
        this.wssSubscription = this.websocketService.getKioskMessages().subscribe((msg) => this.wssRx(msg));
    }

    ngOnDestroy(): void {
        this.wssSubscription?.unsubscribe();
    }

    wssRx(msg: any) {
        if (Object.keys(msg).includes('content')) {
            if (Object.keys(msg).includes('challonge_tournament')) {
                let tournament: ChallongeTournament = <ChallongeTournament>msg['challonge_tournament'];
                if (msg['content'] == 'update' && tournament.id == this.tournament_id) {
                    this.tournament = tournament;
                    this.calculate_displayed_rounds();
                }
            }
            if (Object.keys(msg).includes('challonge_match')) {
                let match: ChallongeMatch = <ChallongeMatch>msg['challonge_match'];
                if (msg['content'] == 'update' && match.tournament_id == this.tournament_id)
                    this.matches.set(match.id, match);
                else if (msg['content'] == 'delete')
                    this.matches.delete(match.id);
            }
            if (Object.keys(msg).includes('challonge_participant')) {
                let participant: ChallongeParticipant = <ChallongeParticipant>msg['challonge_participant'];
                if (msg['content'] == 'update' && participant.tournament_id == this.tournament_id) {
                    if (participant.portrait_id && !this.mediaURLs.has(participant.portrait_id))
                        this.mediaService.getMedia(participant.portrait_id).subscribe((media: Media) => {
                            this.mediaURLs.set(media.id, this.mediaService.getMediaUrl(media))
                        });
                    this.participants.set(participant.id, participant);
                }
                else if (msg['content'] == 'delete')
                    this.participants.delete(participant.id);
            }
        }
    }

    load_tournament(tournament_id: string) {
        this.tournamentService
            .getTournament(tournament_id).subscribe({
                next: (tournament: ChallongeTournament) => {
                    this.matches = new Map<string, ChallongeMatch>;
                    this.participants = new Map<string, ChallongeParticipant>;
                    this.tournament = tournament;
                    this.tournament_id = tournament.id;
                    if (this.title == '') this.title = tournament.name;
                    this.matchService
                        .getMatches().subscribe({
                            next: (matches: ChallongeMatch[]) => {
                                for (let match of matches) {
                                    if (match.tournament_id == tournament_id) this.matches.set(match.id, match);
                                }
                                this.calculate_displayed_rounds();
                            },
                            error: () => {}
                        });
                    this.participantService
                        .getParticipants().subscribe({
                            next: (participants: ChallongeParticipant[]) => {
                                for (let participant of participants) {
                                    if (participant.tournament_id == tournament_id) {
                                        if (participant.portrait_id && !this.mediaURLs.has(participant.portrait_id))
                                            this.mediaService.getMedia(participant.portrait_id).subscribe((media: Media) => {
                                                this.mediaURLs.set(media.id, this.mediaService.getMediaUrl(media))
                                            });
                                        this.participants.set(participant.id, participant);
                                    }
                                }
                            },
                            error: () => {},
                        });
                },
                error: () => {}
            });
    }

    calculate_displayed_rounds() {
        if (this.round && this.signal_completed && this.tournament.completed_rounds.includes(this.round))
            this.finished.emit(null);
        let round: number = 1;
        let round_loser: number | undefined = undefined;
        while (true) {
            if (this.tournament.available_rounds.includes(round)) {
                if (!this.tournament.completed_rounds.includes(round)) break;
            }
            else {
                round = round - 1;
                break;
            }
            round = round + 1;
        }
        if (this.tournament.type == 'double elimination') {
            round_loser = -1;
            while (true) {
                if (this.tournament.available_rounds.includes(round_loser)) {
                    if (!this.tournament.completed_rounds.includes(round_loser)) break;
                }
                else {
                    round_loser = round_loser + 1;
                    break;
                }
                round_loser = round_loser - 1;
            }
            if (round - (round_loser * -1) > 1) round = round_loser * -1 + 1;
        }
        this.round = round;
        this.round_loser = round_loser;
    }

}
