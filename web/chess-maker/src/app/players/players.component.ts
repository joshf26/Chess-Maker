import {Component, Input, OnInit} from '@angular/core';
import {ColorService} from "../services/color/color.service";

@Component({
    selector: 'app-players',
    templateUrl: './players.component.html',
    styleUrls: ['./players.component.less']
})
export class PlayersComponent implements OnInit {
    @Input('serverPlayers') serverPlayers: string[];
    @Input('gamePlayers') gamePlayers: {color: number, nickname: string}[];
    @Input('disableGameTab') disableGameTab: boolean;
    selectedTab: number = 0;

    constructor(
        public colorService: ColorService,
    ) {}

    ngOnInit(): void {}
}
