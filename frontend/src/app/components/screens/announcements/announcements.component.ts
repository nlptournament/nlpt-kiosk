import { CommonModule } from '@angular/common';
import { Component, input, OnDestroy, OnInit } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { Announcement } from '../../../interfaces/announcement';
import { AnnouncementService } from '../../../services/announcement.service';
import { MediaService } from '../../../services/media.service';
import { DiscordPoll } from '../../../interfaces/discord';
import { DiscordService } from '../../../services/discord.service';

@Component({
  selector: 'screen-announcements',
  imports: [CommonModule],
  templateUrl: './announcements.component.html',
  styleUrl: './announcements.component.scss'
})
export class AnnouncementsComponent implements OnInit, OnDestroy {
    isActive = input.required<boolean>();
    header = input.required<string>();
    variables = input.required<any>();

    src_nlpt: boolean = true;
    src_discordpolls: boolean = false;
    type_default: boolean =  true;
    type_danger: boolean =  true;
    type_ffa: boolean =  true;
    discord_guild: string = '';
    discord_channels: string[] = [];

    refreshTimesTimer = timer(1000, 1000);
    refreshTimesTimerSubscription: Subscription | undefined;
    refreshFromBackendsTimer = timer(10000, 10000);
    refreshFromBackendsTimerSubscription: Subscription | undefined;

    announcements: Announcement[] =[];
    polls: DiscordPoll[] = [];

    constructor(
        private announcementService: AnnouncementService,
        private mediaService: MediaService,
        private discordServer: DiscordService
    ) {}

    ngOnInit(): void {
        this.extractVariables();
        this.refreshFromBackends();
        this.refreshFromBackendsTimerSubscription = this.refreshFromBackendsTimer.subscribe(() => this.refreshFromBackends());
        this.refreshTimesTimerSubscription = this.refreshTimesTimer.subscribe(() => this.updateDisplays());
    }

    ngOnDestroy(): void {
        this.refreshTimesTimerSubscription?.unsubscribe();
        this.refreshFromBackendsTimerSubscription?.unsubscribe();
    }

    extractVariables() {
        if (Object.keys(this.variables()).includes('src_nlpt'))
            this.src_nlpt = this.variables()['src_nlpt'];
        if (Object.keys(this.variables()).includes('src_discordpolls'))
            this.src_discordpolls = this.variables()['src_discordpolls'];
        if (Object.keys(this.variables()).includes('type_default'))
            this.type_default = this.variables()['type_default'];
        if (Object.keys(this.variables()).includes('type_danger'))
            this.type_danger = this.variables()['type_danger'];
        if (Object.keys(this.variables()).includes('type_ffa'))
            this.type_ffa = this.variables()['type_ffa'];
        if (Object.keys(this.variables()).includes('discord_guild'))
            this.discord_guild = this.variables()['discord_guild'];
        if (Object.keys(this.variables()).includes('discord_channels'))
            this.discord_channels = this.variables()['discord_channels'];
    }

    refreshFromBackends() {
        if (this.src_nlpt) this.refreshAnnouncements();
        if (this.src_discordpolls) this.refreshPolls();
    }

    refreshAnnouncements() {
        this.announcementService
            .getAnnouncements().subscribe({
                next: (announce: Announcement[]) => {
                    let annos: Announcement[] = [];
                    for (let anno of announce) {
                        if (anno.layout == 'default' && this.type_default) annos.push(anno);
                        if (anno.layout == 'danger' && this.type_danger) annos.push(anno);
                        if (anno.layout == 'ffa' && this.type_ffa) annos.push(anno);
                    }
                    this.updateDisplays(annos);
                },
                error: () => {}
            });
    }

    refreshPolls() {
        this.discordServer
            .getFilteredDiscordPolls(this.discord_channels, this.discord_guild, true).subscribe({
                next: (polls: DiscordPoll[]) => {
                    this.updateDisplays(undefined, polls);
                },
                error: () => {}
            });
    }

    updateDisplays(announce: Announcement[] | undefined = undefined, polls: DiscordPoll[] | undefined = undefined) {
        for (let anno of (announce ? announce : this.announcements)) {
            if (anno.target) {
                let diff: number = anno.target - Date.now() / 1000;
                if (Math.floor(diff) <= 0) anno.display_time = 'jetzt';
                else {
                    let h: number = Math.floor(diff / 3600);
                    diff = diff % 3600;
                    let m: number = Math.floor(diff / 60);
                    let s: number = Math.floor(diff % 60);
                    anno.display_time = (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
                }
            } else anno.display_time = null;
            if (anno.img) {
                anno.img_url = this.mediaService.getMediaUrl(undefined, anno.img);
            } else  anno.img_url = null;
        }
        if (announce) this.announcements = announce;

        for (let poll of (polls ? polls : this.polls)) {
            if (poll.till_ts) {
                let diff: number = poll.till_ts - Date.now() / 1000;
                if (Math.floor(diff) <= 0) poll.active = false;
                else {
                    let h: number = Math.floor(diff / 3600);
                    diff = diff % 3600;
                    let m: number = Math.floor(diff / 60);
                    let s: number = Math.floor(diff % 60);
                    poll.display_time = (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
                }
            } else poll.display_time = null;
        }
        if (polls) this.polls = polls;
    }
}
