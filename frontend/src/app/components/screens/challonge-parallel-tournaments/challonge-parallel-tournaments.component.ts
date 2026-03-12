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
  selector: 'screen-challonge-parallel-tournaments',
  imports: [CommonModule, FontAwesomeModule],
  templateUrl: './challonge-parallel-tournaments.component.html',
  styleUrl: './challonge-parallel-tournaments.component.scss'
})
export class ChallongeParallelTournamentsComponent {
    faBoltLightning = faBoltLightning;
    isActive = input.required<boolean>();
    header = input.required<string>();
    variables = input.required<any>();
    finished = output<null>();

    wssSubscription: Subscription | undefined;
    tournament1!: ChallongeTournament;
    tournament2!: ChallongeTournament;
    matches: Map<string, ChallongeMatch> = new Map<string, ChallongeMatch>;
    participants: Map<string, ChallongeParticipant> = new Map<string, ChallongeParticipant>;
    mediaURLs: Map<string, string> = new Map<string, string>;

    tournament1_id: string | undefined;
    tournament2_id: string | undefined;
    title: string | undefined;
    signal_completed: boolean = false;
    t1_round: number | undefined;
    t1_round_loser: number | undefined;
    t2_round: number | undefined;
    t2_round_loser: number | undefined;

    constructor(
        private websocketService: WebSocketService,
        private tournamentService: ChallongeTournamentService,
        private matchService: ChallongeMatchService,
        private participantService: ChallongeParticipantService,
        private mediaService: MediaService
    ) {}

    ngOnInit() {
        if (Object.keys(this.variables()).includes('tournament1_id')) this.tournament1_id = this.variables()['tournament1_id'];
        if (Object.keys(this.variables()).includes('tournament2_id')) this.tournament2_id = this.variables()['tournament2_id'];
        this.load_tournaments();
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
                if (msg['content'] == 'update') {
                    if (tournament.id == this.tournament1_id) {
                        this.tournament1 = tournament;
                        this.calculate_displayed_rounds(tournament);
                    }
                    if (tournament.id == this.tournament2_id) {
                        this.tournament2 = tournament;
                        this.calculate_displayed_rounds(tournament);
                    }
                }
            }
            if (Object.keys(msg).includes('challonge_match')) {
                let match: ChallongeMatch = <ChallongeMatch>msg['challonge_match'];
                if (msg['content'] == 'update' && (match.tournament_id == this.tournament1_id || match.tournament_id == this.tournament2_id))
                    this.matches.set(match.id, match);
                else if (msg['content'] == 'delete')
                    this.matches.delete(match.id);
            }
            if (Object.keys(msg).includes('challonge_participant')) {
                let participant: ChallongeParticipant = <ChallongeParticipant>msg['challonge_participant'];
                if (msg['content'] == 'update' && (participant.tournament_id == this.tournament1_id || participant.tournament_id == this.tournament2_id)) {
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

    load_tournaments() {
        if (this.tournament1_id && this.tournament2_id) {
            this.matches = new Map<string, ChallongeMatch>;
            this.participants = new Map<string, ChallongeParticipant>;
            this.tournamentService
                .getTournament(this.tournament1_id).subscribe({
                    next: (tournament: ChallongeTournament) => {
                        this.tournament1 = tournament;
                        this.tournamentService
                            .getTournament(this.tournament2_id!).subscribe({
                                next: (tournament: ChallongeTournament) => {
                                    this.tournament2 = tournament;
                                    this.matchService
                                        .getMatches().subscribe({
                                            next: (matches: ChallongeMatch[]) => {
                                                for (let match of matches) {
                                                    if (match.tournament_id == this.tournament1_id || match.tournament_id == this.tournament2_id) this.matches.set(match.id, match);
                                                }
                                                this.calculate_displayed_rounds(this.tournament1);
                                                this.calculate_displayed_rounds(this.tournament2);
                                            },
                                            error: () => {}
                                        });
                                    this.participantService
                                        .getParticipants().subscribe({
                                            next: (participants: ChallongeParticipant[]) => {
                                                for (let participant of participants) {
                                                    if (participant.tournament_id == this.tournament1_id || participant.tournament_id == this.tournament2_id) {
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
                    },
                    error: () => {}
                });
        }
    }

    calculate_displayed_rounds(tournament: ChallongeTournament) {
        if (this.signal_completed && this.t1_round && this.t2_round &&
            this.tournament1.completed_rounds.includes(Math.min(this.t1_round, this.t2_round)) &&
            this.tournament2.completed_rounds.includes(Math.min(this.t1_round, this.t2_round)))
                this.finished.emit(null);
        let round: number = 1;
        let round_loser: number | undefined = undefined;
        while (true) {
            if (tournament.available_rounds.includes(round)) {
                if (!tournament.completed_rounds.includes(round)) break;
            }
            else {
                round = round - 1;
                break;
            }
            round = round + 1;
        }
        if (tournament.type == 'double elimination') {
            round_loser = -1;
            while (true) {
                if (tournament.available_rounds.includes(round_loser)) {
                    if (!tournament.completed_rounds.includes(round_loser)) break;
                }
                else {
                    round_loser = round_loser + 1;
                    break;
                }
                round_loser = round_loser - 1;
            }
            if (round - (round_loser * -1) > 1) round = round_loser * -1 + 1;
        }
        if (tournament.id == this.tournament1_id) {
            this.t1_round = round;
            this.t1_round_loser = round_loser;
        }
        else {
            this.t2_round = round;
            this.t2_round_loser = round_loser;
        }
    }
}
