import {Component, OnInit} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {PiecesService} from '../services/pieces/pieces.service';


const COLOR_NAMES = [
    'White',
    'Black',
    'Red',
    'Orange',
    'Yellow',
    'Green',
    'Blue',
    'Purple',
]


interface GameMetaData {
    name: string,
    creator: string,
    board: string,
    available_colors: number[],
    total_players: number,
}

@Component({
    selector: 'app-lobby',
    templateUrl: './lobby.component.html',
    styleUrls: ['./lobby.component.less']
})
export class LobbyComponent implements OnInit {
    games: {[key: string]: GameMetaData};
    selectedGameId: string;
    colorNames = COLOR_NAMES;

    constructor(
        private api: ApiService,
        private piecesService: PiecesService,
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
        this.piecesService.updatePieceTypes(parameters.pieces);
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

        this.selectedGameId = gameId;
    }
}
