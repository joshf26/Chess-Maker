import {Component, OnInit} from '@angular/core';


interface GameData {
    name: string,
    creator: string,
    board: string,
    slots: number,
    filled: number,
}


@Component({
    selector: 'app-lobby',
    templateUrl: './lobby.component.html',
    styleUrls: ['./lobby.component.less']
})
export class LobbyComponent implements OnInit {
    games: GameData[] = [
        {name: 'My First Game', creator: 'Josh', board: 'Standard 8x8', slots: 2, filled: 0},
        {name: 'My Second Game', creator: 'Josh', board: 'Standard 4x4', slots: 2, filled: 1},
    ];

    constructor() {}

    ngOnInit(): void {
    }
}
