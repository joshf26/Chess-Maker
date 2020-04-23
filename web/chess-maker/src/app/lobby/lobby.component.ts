import {Component, OnInit} from '@angular/core';
import {ApiService} from '../api.service';


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

    constructor(private api: ApiService) {
        api.getCommand('update_game_metadata').subscribe(this.updateGameMetadata);
    }

    ngOnInit(): void {
        this.api.run('get_games', {});
    }

    updateGameMetadata(gameData: {[key: string]: GameData}) {
        console.log('Received the following game data!!!');
        console.log(gameData);
    }

    showGame(game: any) {
        alert(`showing game ${game}`);
    }
}
