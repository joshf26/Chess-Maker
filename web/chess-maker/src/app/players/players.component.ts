import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-players',
    templateUrl: './players.component.html',
    styleUrls: ['./players.component.less']
})
export class PlayersComponent implements OnInit {
    @Input('serverPlayers') serverPlayers: string[];
    selectedTab: number = 0;

    constructor() {}

    ngOnInit(): void {}
}
