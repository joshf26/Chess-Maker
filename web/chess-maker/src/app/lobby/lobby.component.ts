import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import {ApiService} from '../api.service';


interface GameMetaData {
    name: string,
    creator: string,
    board: string,
    current_players: number,
    total_players: number,
}


@Component({
    selector: 'app-lobby',
    templateUrl: './lobby.component.html',
    styleUrls: ['./lobby.component.less']
})
export class LobbyComponent implements OnInit {
    games: {[key: string]: GameMetaData};

    constructor(
        private api: ApiService,
        private changeDetector: ChangeDetectorRef,
    ) {
        api.getCommand('update_game_metadata').subscribe(this.updateGameMetadata.bind(this));
    }

    ngOnInit(): void {
        this.api.run('get_games', {});
    }

    updateGameMetadata(parameters: {[key: string]: any}): void {
        this.games = parameters.game_metadata;
        this.changeDetector.detectChanges();
        console.log(this.games);
    }

    createGame(): void {
        this.api.run('create_game', {
            name: 'My Cool Game',
            pack: 'standard',
            board: 'Standard8x8',
        })
    }

    showGame(game: any): void {
        alert(`showing game ${game}`);
    }
}
