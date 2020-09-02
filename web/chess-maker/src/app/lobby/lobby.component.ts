import {ChangeDetectorRef, Component, OnInit, ViewChild} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {Controller, Pack} from '../services/pack/pack.service';
import {MatDialog} from '@angular/material/dialog';
import {Router} from '@angular/router';
import {Color, ColorService} from "../services/color/color.service";
import {CreateGameDialog} from "./create-game-dialog/create-game-dialog.component";
import {Game, GameService, Ply, Vector2} from "../services/game/game.service";
import {Player, PlayerService} from "../services/player/player.service";
import {GameComponent} from "../game/game.component";
import {SidebarService} from "../services/sidebar/sidebar.service";
import {MatSidenav} from "@angular/material/sidenav";
import {PlayersListComponent} from "./players-list/players-list.component";
import {SelectPlyDialog} from "./select-ply-dialog/select-ply-dialog.component";
import {GamesListComponent} from "./games-list/games-list.component";
import {ChatComponent} from "./chat/chat.component";
import {MatSnackBar} from "@angular/material/snack-bar";
import {UrlService} from "../services/url/url.service";
import {FocusGameParameters} from "../services/api/commands/focus-game-command";
import {CommandService, Subjects} from "../services/api/command.service";
import {OfferPliesParameters} from "../services/api/commands/offer-plies-command";

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
    @ViewChild('playersListComponent') private playersListComponent: PlayersListComponent;
    @ViewChild('chatComponent') private chatComponent: ChatComponent;
    @ViewChild('gamesListComponent') gamesListComponent: GamesListComponent;
    @ViewChild('gameComponent') gameComponent: GameComponent;
    @ViewChild('sidebar') sidebar: MatSidenav;

    players: Player[];

    constructor(
        public createGameDialog: MatDialog,
        public selectPlyDialog: MatDialog,
        public apiService: ApiService,
        public playerService: PlayerService,
        public colorService: ColorService,
        public gameService: GameService,
        public sidebarService: SidebarService,
        private changeDetectorRef: ChangeDetectorRef,
        private router: Router,
        private snackBar: MatSnackBar,
        private urlService: UrlService,
        commandService: CommandService,
    ) {
        commandService.ready.subscribe((subjects: Subjects) => {
            subjects.focusGame.subscribe(this.focusGame);
            subjects.offerPlies.subscribe(this.offerPlies);
        });

        apiService.onForceDisconnect.subscribe(reason => {
            this.selectPlyDialog.closeAll();
            this.createGameDialog.closeAll();
            this.snackBar.open(reason, 'Ok', {
                duration: undefined,
                horizontalPosition: 'end',
                panelClass: 'error',
            })
        });

        urlService.joinFromUrl.subscribe(this.showGame.bind(this));
    }

    private offerPlies = (parameters: OfferPliesParameters): void => {
        this.selectPlyDialog.open(SelectPlyDialog, {
            data: {
                game: this.gameService.selectedGame,
                from: parameters.from,
                to: parameters.to,
                plies: parameters.plies,
            },
        });
    };

    private focusGame = (parameters: FocusGameParameters): void => {
        this.showGame(parameters.game);
    };

    ngOnInit() {
        if (!this.apiService.isConnected()) {
            this.router.navigate(['/']);
        }
    }

    ngAfterViewInit() {
        this.sidebarService.registerSidenav(this.sidebar);
    }

    disconnect() {
        this.apiService.disconnect();
        this.router.navigate(['/']);
    }

    createGame(): void {
        this.createGameDialog.open(CreateGameDialog, {
            data: {
                displayName: 'New Game',
                public: true,
            },
        });
    }

    showGame(game?: Game): void {
        if (game) {
            this.apiService.showGame(game);
        }

        this.gameService.setSelectedGame(game);
        this.changeDetectorRef.detectChanges();

        // Switch to the "Game" tab.
        this.playersListComponent.selectedTab = 1;
        this.chatComponent.selectedTab = 1;
    }

    joinGame(game: Game, color: Color): void {
        this.apiService.joinGame(game, color);
        this.gamesListComponent.loading = true;
        setTimeout(() => {
            // Switch to the "My Games" tab.
            this.gamesListComponent.loading = false;
            this.gamesListComponent.selectedTab = 1;

            // Switch to the "Game" tab.
            this.playersListComponent.selectedTab = 1;
            this.chatComponent.selectedTab = 1;
        }, 500);
    }

    leaveGame(game: Game): void {
        this.apiService.leaveGame(game);
        this.gamesListComponent.loading = true;
        setTimeout(() => {
            // Switch to the "Public" tab.
            this.gamesListComponent.loading = false;
            this.gamesListComponent.selectedTab = 0;
        }, 500);
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
        result += ' win!';

        return result;
    }
}

