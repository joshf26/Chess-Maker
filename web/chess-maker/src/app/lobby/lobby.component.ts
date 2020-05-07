import {Component, ElementRef, Inject, OnInit, ViewChild} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {PackDataService} from '../services/pieces/pack-data.service';
import {MAT_DIALOG_DATA, MatDialog, MatDialogRef} from '@angular/material/dialog';

const COLOR_NAMES = [
    'White',
    'Black',
    'Red',
    'Orange',
    'Yellow',
    'Green',
    'Blue',
    'Purple',
];

export interface GameMetaData {
    name: string,
    creator: string,
    board: string,
    available_colors: number[],
    total_players: number,
    playing_as?: number,
}

export interface CreateGameDialogData {
    name: string,
    board: {pack: string, name: string},
}

@Component({
    selector: 'app-lobby',
    templateUrl: './lobby.component.html',
    styleUrls: ['./lobby.component.less']
})
export class LobbyComponent implements OnInit {
    games: {[key: string]: GameMetaData};
    hasNotification: {[key: string]: boolean} = {};
    selectedGameId: string;
    colorNames = COLOR_NAMES;

    constructor(
        public dialog: MatDialog,
        public api: ApiService,
        private packDataService: PackDataService,
    ) {
        api.getCommand('update_game_metadata').subscribe(this.updateGameMetadata.bind(this));
        api.getCommand('update_pack_data').subscribe(this.updatePackData.bind(this));
    }

    ngOnInit(): void {
        this.api.run('get_games', {});
    }

    updateGameMetadata(parameters: {[key: string]: any}): void {
        this.games = parameters.game_metadata;

        if (!this.games.hasOwnProperty(this.selectedGameId)) {
            this.selectedGameId = '';
        }
    }

    updatePackData(parameters: {[key: string]: any}): void {
        this.packDataService.updatePackData(parameters.pack_data);
    }

    notify(gameId: string) {
        this.hasNotification[gameId] = true;
        console.log(`${gameId} has a move.`);
    }

    createGame(): void {
        this.dialog.open(CreateGameDialog, {
            data: {
                name: 'New Game',
                board: {pack: '', name: ''},
            },
        });
    }

    showGame(gameId: string): void {
        this.api.run('subscribe_to_game', {
            game_id: gameId,
        })

        this.hasNotification[gameId] = false;
        this.selectedGameId = gameId;
    }

    joinGame(gameId: string, color: number): void {
        console.log(`Joining game ${gameId} as ${this.colorNames[color]}.`);
        this.api.run('join_game', {
            game_id: gameId,
            color: color,
        })
    }
}

@Component({
    selector: 'create-game-dialog',
    templateUrl: 'create-game.dialog.html',
})
export class CreateGameDialog {
    constructor(
        public packDataService: PackDataService,
        public api: ApiService,
        @Inject(MAT_DIALOG_DATA) public data: CreateGameDialogData,
    ) {}

    createGame(): void {
        this.api.run('create_game', {
            name: this.data.name,
            pack: this.data.board.pack,
            board: this.data.board.name,
        })
    }
}
