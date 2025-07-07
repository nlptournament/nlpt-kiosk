import { Component, input, OnInit } from '@angular/core';
import { ChallongeTournamentService } from '../../../services/challonge-tournament.service';
import { ChallongeMatchService } from '../../../services/challonge-match.service';
import { ChallongeParticipantService } from '../../../services/challonge-participant.service';
import { MediaService } from '../../../services/media.service';
import { ChallongeTournament } from '../../../interfaces/challonge-tournament';
import { ChallongeMatch } from '../../../interfaces/challonge-match';
import { ChallongeParticipant } from '../../../interfaces/challonge-participant';
import { Media } from '../../../interfaces/media';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'screen-challonge-round-completion',
  imports: [CommonModule],
  templateUrl: './challonge-round-completion.component.html',
  styleUrl: './challonge-round-completion.component.scss'
})
export class ChallongeRoundCompletionComponent implements OnInit {
    isActive = input.required<boolean>();
    variables = input.required<any>();

    tournament!: ChallongeTournament;
    matches: Map<string, ChallongeMatch> = new Map<string, ChallongeMatch>;
    participants: Map<string, ChallongeParticipant> = new Map<string, ChallongeParticipant>;
    media: Map<string, Media> = new Map<string, Media>;

    round: number | undefined;
    round_loser: number | undefined;

    constructor(
        private tournamentService: ChallongeTournamentService,
        private matchService: ChallongeMatchService,
        private participantService: ChallongeParticipantService,
        private mediaService: MediaService
    ) {}

    ngOnInit() {
        if (Object.keys(this.variables()).includes('tournament_id')) this.load_tournament(this.variables()['tournament_id']);
    }

    load_tournament(tournament_id: string) {
        this.tournamentService
            .getTournament(tournament_id).subscribe({
                next: (tournament: ChallongeTournament) => {
                    this.matches = new Map<string, ChallongeMatch>;
                    this.participants = new Map<string, ChallongeParticipant>;
                    this.tournament = tournament;
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
                                        if (participant.portrait_id && !this.media.has(participant.portrait_id))
                                            this.mediaService.getMedia(participant.portrait_id).subscribe((media: Media) => {
                                                this.media.set(media.id, media)
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
            }
            if (round - (round_loser * -1) > 1) round = round_loser * -1 + 1;
        }
        this.round = round;
        this.round_loser = round_loser;
    }

}
