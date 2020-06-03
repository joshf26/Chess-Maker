import {ChangeDetectorRef, Component, Inject, OnInit, ViewChild} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {PackDataService} from '../services/pieces/pack-data.service';
import {MAT_DIALOG_DATA, MatDialog} from '@angular/material/dialog';
import {BoardComponent, WinnerData} from '../board/board.component';
import {Router} from '@angular/router';
import {PlayersComponent} from "../players/players.component";
import {ColorService} from "../services/color/color.service";

export interface GameMetaData {
    name: string,
    creator: string,
    pack: string,
    board: string,
    players: {
        nickname: string,
        color: number,
    }[],
    total_players: number,
    playing_as?: number,
}

export interface CreateGameDialogData {
    name: string,
    board: {pack: string, name: string},
}

export interface Ply {
    name: string,
    actions: object[],
}

export interface SelectPlyDialogData {
    fromRow: number,
    fromCol: number,
    toRow: number,
    toCol: number,
    plies: Ply[],
    gameId: string,
}

@Component({
    selector: 'app-lobby',
    templateUrl: './lobby.component.html',
    styleUrls: ['./lobby.component.less']
})
export class LobbyComponent implements OnInit {
    @ViewChild('board') private board: BoardComponent;
    @ViewChild('playersComponent') private playersComponent: PlayersComponent;
    games: {[key: string]: GameMetaData};
    availableColors: number[];
    players: string[];
    hasNotification: {[key: string]: boolean} = {};
    selectedGameId: string;
    winnerData?: WinnerData = null;

    constructor(
        public createGameDialog: MatDialog,
        public selectPlyDialog: MatDialog,
        public api: ApiService,
        public colorService: ColorService,
        public packDataService: PackDataService,
        private changeDetectorRef: ChangeDetectorRef,
        private router: Router,
    ) {
        api.getCommand('update_metadata').subscribe(this.updateMetadata.bind(this));
        api.getCommand('update_pack_data').subscribe(this.updatePackData.bind(this));
        api.getCommand('plies').subscribe(this.showPlies.bind(this));
        api.getCommand('focus_game').subscribe(this.focusGame.bind(this));
    }

    ngOnInit(): void {}

    updateAvailableColors(): void {
        if (!this.selectedGameId) {
            return;
        }

        this.availableColors = [...this.packDataService.boardTypes[this.games[this.selectedGameId].pack][this.games[this.selectedGameId].board].colors];
        for (const player of this.games[this.selectedGameId].players) {
            this.availableColors.splice(this.availableColors.indexOf(player.color), 1);
        }
    }

    updateMetadata(parameters: {[key: string]: any}): void {
        this.players = parameters.players;
        this.games = parameters.game_metadata;

        if (!this.games.hasOwnProperty(this.selectedGameId)) {
            this.selectedGameId = '';
        }

        this.updateAvailableColors();
    }

    updatePackData(parameters: {[key: string]: any}): void {
        this.packDataService.updatePackData(parameters.pack_data);
    }

    showPlies(parameters: {[key: string]: any}): void {
        this.selectPlyDialog.open(SelectPlyDialog, {
            data: {
                fromRow: parameters.from_row,
                fromCol: parameters.from_col,
                toRow: parameters.to_row,
                toCol: parameters.to_col,
                plies: parameters.plies,
                gameId: this.selectedGameId,
            },
        });
    }

    focusGame(parameters: {[key: string]: any}): void {
        this.showGame(parameters.game_id);
    }

    disconnect() {
        this.api.disconnect();
        this.router.navigate(['/']);
    }

    notify(gameId: string) {
        this.hasNotification[gameId] = true;
    }

    createGame(): void {
        this.createGameDialog.open(CreateGameDialog, {
            data: {
                name: 'New Game',
                board: {pack: '', name: ''},
            },
        });
    }

    showGame(gameId: string): void {
        this.api.run('show_game', {
            game_id: gameId,
        })

        this.hasNotification[gameId] = false;
        this.selectedGameId = gameId;
        this.updateAvailableColors();
        this.changeDetectorRef.detectChanges();
        this.board.updateBoardSize();

        // Switch to the "Game" tab.
        this.playersComponent.selectedTab = 1;
    }

    joinGame(gameId: string, color: number): void {
        this.api.run('join_game', {
            game_id: gameId,
            color: color,
        })
    }

    onWinner(winnerData: WinnerData): void {
        this.winnerData = winnerData;
    }

    winner_string(colors: number[]): string {
        if (colors.length == 0) {
            return 'No winners!';
        }

        if (colors.length == 1) {
            return `${this.colorService.names[colors[0]]} wins!`;
        }

        if (colors.length == 2) {
            return `${this.colorService.names[colors[0]]} and ${this.colorService.names[colors[1]]} win!`;
        }

        let result = '';
        for (const [index, color] of Object.entries(colors)) {
            result += parseInt(index) == colors.length - 1 ? `and ${this.colorService.names[color]}` : `${this.colorService.names[color]}, `;
        }
        result += ' win!'

        return result;
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

@Component({
    selector: 'select-ply-dialog',
    templateUrl: 'select-ply.dialog.html',
})
export class SelectPlyDialog {
    constructor(
        public api: ApiService,
        @Inject(MAT_DIALOG_DATA) public data: SelectPlyDialogData,
    ) {}

    selectPly(ply: Ply): void {
        this.api.run('submit_ply', {
            game_id: this.data.gameId,
            from_row: this.data.fromRow,
            from_col: this.data.fromCol,
            to_row: this.data.toRow,
            to_col: this.data.toCol,
            ply: ply,
        })
    }
}
