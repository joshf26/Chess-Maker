import {Component, OnInit} from '@angular/core';
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
    pieces: {[key: string]: {[key: string]: {image: HTMLImageElement}}} = {};

    constructor(
        private api: ApiService,
    ) {
        api.getCommand('update_game_metadata').subscribe(this.updateGameMetadata.bind(this));
        api.getCommand('update_pieces').subscribe(this.updatePieces.bind(this));
    }

    ngOnInit(): void {
        this.api.run('get_games', {});
    }

    updateGameMetadata(parameters: {[key: string]: any}): void {
        this.games = parameters.game_metadata;
    }

    updatePieces(parameters: {[key: string]: any}): void {
        for (let [pack, packData] of Object.entries(parameters.pieces)) {
            for (let [piece, pieceData] of Object.entries(packData)) {
                const image = new Image();
                image.src = `data:image/svg+xml,${pieceData.image}`;

                if (!this.pieces.hasOwnProperty(pack)) {
                    this.pieces[pack] = {};
                }

                this.pieces[pack][piece] = {image: image};
            }
        }

        console.log('Piece data', this.pieces);
    }

    createGame(): void {
        this.api.run('create_game', {
            name: 'My Cool Game',
            pack: 'standard',
            board: 'Standard8x8',
        })
    }

    showGame(gameId: string): void {
        this.api.run('subscribe_to_game', {
            game_id: gameId,
        })
    }
}
