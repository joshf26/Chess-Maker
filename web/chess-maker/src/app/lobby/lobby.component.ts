import {ChangeDetectorRef, Component, Inject, OnInit, ViewChild} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {Controller, Pack, PackService} from '../services/pack/pack.service';
import {MAT_DIALOG_DATA, MatDialog} from '@angular/material/dialog';
import {Router} from '@angular/router';
import {PlayersComponent} from "../players/players.component";
import {Color, ColorService} from "../services/color/color.service";
import {CreateGameDialog} from "./create-game-dialog.component";
import {Game, GameService, Ply, Vector2} from "../services/game/game.service";
import {Player, PlayerService} from "../services/player/player.service";
import {GameComponent} from "../game/game.component";
import {SidebarService} from "../services/sidebar/sidebar.service";
import {MatSidenav} from "@angular/material/sidenav";

export interface CreateGameDialogData {
    displayName: string,
    public: boolean,
    pack?: Pack,
    controller?: Controller,
    password?: string,
}

export interface SelectPlyDialogData {
    game: Game,
    from: Vector2,
    to: Vector2,
    plies: Ply[],
}

@Component({
    selector: 'app-lobby',
    templateUrl: './lobby.component.html',
    styleUrls: ['./lobby.component.less'],
})
export class LobbyComponent implements OnInit {
    @ViewChild('playersComponent') private playersComponent: PlayersComponent;
    @ViewChild('gameComponent') gameComponent: GameComponent;
    @ViewChild('sidebar') sidebar: MatSidenav;

    availableColors: number[];
    players: Player[];
    hasNotification: {[key: string]: boolean} = {};
    selectedGame: Game;

    constructor(
        public createGameDialog: MatDialog,
        public selectPlyDialog: MatDialog,
        public apiService: ApiService,
        public gameService: GameService,
        public playerService: PlayerService,
        public colorService: ColorService,
        public sidebarService: SidebarService,
        private changeDetectorRef: ChangeDetectorRef,
        private router: Router,
    ) {
        apiService.handlers.offerPlies = this.offerPlies.bind(this);
        apiService.handlers.focusGame = this.showGame.bind(this);
    }

    ngOnInit() {
        if (!this.apiService.isConnected()) {
            this.router.navigate(['/']);
        }
    }

    ngAfterViewInit() {
        this.sidebarService.registerSidenav(this.sidebar);
    }

    private updateAvailableColors(): void {
        if (!this.selectedGame) {
            return;
        }

        this.availableColors = [...this.selectedGame.metadata.controller.colors];
        for (const color of Object.keys(this.selectedGame.metadata.players)) {
            this.availableColors.splice(this.availableColors.indexOf(Number(color)), 1);
        }
    }

    private offerPlies(from: Vector2, to: Vector2, plies: Ply[]): void {
        this.selectPlyDialog.open(SelectPlyDialog, {
            data: {
                game: this.selectedGame,
                from: from,
                to: to,
                plies: plies,
            },
        });
    }

    disconnect() {
        this.apiService.disconnect();
        this.router.navigate(['/']);
    }

    notify(gameId: string) {
        this.hasNotification[gameId] = true;
    }

    createGame(): void {
        this.createGameDialog.open(CreateGameDialog, {
            data: {
                displayName: 'New Game',
                public: true,
            },
        });
    }

    showGame(game: Game): void {
        this.apiService.showGame(game);

        this.hasNotification[game.id] = false;
        this.selectedGame = game;
        this.updateAvailableColors();
        this.changeDetectorRef.detectChanges();

        // Switch to the "Game" tab.
        this.playersComponent.selectedTab = 1;
    }

    joinGame(game: Game, color: Color): void {
        this.apiService.joinGame(game, color);
    }

    winnerString(colors: number[]): string {
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
    selector: 'select-ply-dialog',
    templateUrl: 'select-ply.dialog.html',
})
export class SelectPlyDialog {
    constructor(
        public api: ApiService,
        @Inject(MAT_DIALOG_DATA) public data: SelectPlyDialogData,
    ) {}

    selectPly(ply: Ply): void {
        this.api.submitPly(
            this.data.game,
            this.data.from,
            this.data.to,
            ply,
        );
    }
}
