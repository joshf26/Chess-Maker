import {ChangeDetectorRef, Component, Inject, OnInit, ViewChild} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {PackDataService} from '../services/pieces/pack-data.service';
import {MAT_DIALOG_DATA, MatDialog} from '@angular/material/dialog';
import {BoardComponent, WinnerData} from '../board/board.component';
import {Router} from '@angular/router';

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
    pack: string,
    board: string,
    available_colors: number[],
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
    games: {[key: string]: GameMetaData};
    hasNotification: {[key: string]: boolean} = {};
    selectedGameId: string;
    colorNames = COLOR_NAMES;
    winnerData?: WinnerData = null;

    constructor(
        public createGameDialog: MatDialog,
        public selectPlyDialog: MatDialog,
        public api: ApiService,
        private packDataService: PackDataService,
        private changeDetectorRef: ChangeDetectorRef,
        private router: Router,
    ) {
        api.getCommand('update_game_metadata').subscribe(this.updateGameMetadata.bind(this));
        api.getCommand('update_pack_data').subscribe(this.updatePackData.bind(this));
        api.getCommand('plies').subscribe(this.showPlies.bind(this));
    }

    ngOnInit(): void {}

    updateGameMetadata(parameters: {[key: string]: any}): void {
        this.games = parameters.game_metadata;

        if (!this.games.hasOwnProperty(this.selectedGameId)) {
            this.selectedGameId = '';
        }
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
        this.changeDetectorRef.detectChanges();
        this.board.updateBoardSize();
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
            return `${COLOR_NAMES[colors[0]]} wins!`;
        }

        if (colors.length == 2) {
            return `${COLOR_NAMES[colors[0]]} and ${COLOR_NAMES[colors[1]]} win!`;
        }

        let result = '';
        for (const [index, color] of Object.entries(colors)) {
            result += index == colors.length - 1 ? `and ${COLOR_NAMES[color]}` : `${COLOR_NAMES[color]}, `;
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
