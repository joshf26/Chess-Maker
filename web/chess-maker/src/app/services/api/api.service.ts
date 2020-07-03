import {Injectable} from '@angular/core';
import {webSocket, WebSocketSubject} from 'rxjs/webSocket';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {map, filter} from 'rxjs/operators';
import {Controller, DecoratorType, Pack, PackService, PieceType} from "../pack/pack.service";
import {Color} from "../color/color.service";
import {
    Action,
    Decorator, Direction,
    Game, GameData, GameMetadata,
    GameService,
    InfoElement,
    InventoryItem,
    Piece,
    Ply,
    Vector2, WinnerData
} from "../game/game.service";
import {
    RawFocusGameParameters, RawOfferPliesParameters, RawSetPlayerParameters, RawShowErrorParameters,
    RawUpdateGameDataParameters, RawUpdateGameMetadataParameters,
    RawUpdatePackDataParameters, RawUpdatePlayersParameters
} from "./parameter-types";
import {Player, PlayerService} from "../player/player.service";
import {MatSnackBar} from "@angular/material/snack-bar";

@Injectable({
    providedIn: 'root',
})
export class ApiService {
    private socket: WebSocketSubject<unknown>;
    private commands: Observable<unknown>;

    public handlers: {
        setPlayer: (player: Player) => void,
        focusGame: (game: Game) => void,
        updatePackData: (packs: {[key: string]: Pack}) => void,
        updateGameMetadata: (games: {[key: string]: GameMetadata}) => void,
        updatePlayers: (players: {[key: string]: Player}) => void,
        updateGameData: (id: string, data: GameData) => void,
        offerPlies: (from: Vector2, to: Vector2, plies: Ply[]) => void,
    } = {
        setPlayer: () => {},
        focusGame: () => {},
        updatePackData: () => {},
        updatePlayers: () => {},
        updateGameMetadata: () => {},
        updateGameData: () => {},
        offerPlies: () => {},
    };

    constructor(
        private router: Router,
        private gameService: GameService,
        private packService: PackService,
        private playerService: PlayerService,
        private snackBar: MatSnackBar,
    ) {
        this.handlers.updatePackData = packService.updatePackData.bind(packService);
        this.handlers.updatePlayers = playerService.updatePlayers.bind(playerService);
        this.handlers.setPlayer = playerService.setPlayer.bind(playerService);
        this.handlers.updateGameMetadata = gameService.updateGameMetadata.bind(gameService);
        this.handlers.updateGameData = gameService.updateGameData.bind(gameService);
    }

    private run(command: string, parameters: {[key: string]: any}): void {
        this.socket.next({
            command: command,
            parameters: parameters,
        });
    }

    private setPlayer(parameters: RawSetPlayerParameters): void {
        const player = this.playerService.get(parameters.id);
        this.handlers.setPlayer(player);
    }

    private focusGame(parameters: RawFocusGameParameters): void {
        const game = this.gameService.get(parameters.game_id);
        this.handlers.focusGame(game);
    }

    private updatePackData(parameters: RawUpdatePackDataParameters): void {
        const packs: {[key: string]: Pack} = {};

        for (const [packId, rawPack] of Object.entries(parameters.packs)) {
            packs[packId] = new Pack(
                packId,
                rawPack.display_name,
                {},
                {},
                {},
            );

            for (const [controllerId, controller] of Object.entries(rawPack.controllers)) {
                packs[packId].controllers[controllerId] = new Controller(
                    controllerId,
                    controller.displayName,
                    packs[packId],
                    new Vector2(controller.rows, controller.cols),
                    controller.colors,
                    controller.options,
                );
            }

            for (const [pieceTypeId, pieceType] of Object.entries(rawPack.pieces)) {
                packs[packId].pieceTypes[pieceTypeId] = new PieceType(
                    pieceTypeId,
                    packs[packId],
                    pieceType.image,
                );
            }

            for (const [decoratorTypeId, decoratorType] of Object.entries(rawPack.decorators)) {
                packs[packId].decoratorTypes[decoratorTypeId] = new DecoratorType(
                    decoratorTypeId,
                    packs[packId],
                    decoratorType.image,
                );
            }
        }

        this.handlers.updatePackData(packs);
    }

    private updatePlayers(parameters: RawUpdatePlayersParameters): void {
        const players: {[key: string]: Player} = {};

        for (const [playerId, rawPlayer] of Object.entries(parameters.players)) {
            players[playerId] = new Player(
                playerId,
                rawPlayer.displayName,
            );
        }

        this.handlers.updatePlayers(players);
    }

    private updateGameMetadata(parameters: RawUpdateGameMetadataParameters): void {
        const games: {[key: string]: GameMetadata} = {};

        for (const [id, rawGame] of Object.entries(parameters.game_metadata)) {
            const players: {[color in Color]?: Player} = {};

            for (const [color, playerId] of Object.entries(rawGame.players)) {
                players[color] = this.playerService.get(playerId);
            }

            games[id] = new GameMetadata(
                rawGame.displayName,
                this.playerService.get(rawGame.creator),
                this.packService.getController(rawGame.controller_pack_id, rawGame.controller_id),
                players,
            );
        }

        this.handlers.updateGameMetadata(games);
    }

    private updateGameData(parameters: RawUpdateGameDataParameters): void {
        const pieces: Piece[] = [];
        const decorators: Decorator[] = [];
        const infoElements: InfoElement[] = [];
        const inventoryItems: InventoryItem[] = [];

        for (const rawPiece of parameters.pieces) {
            pieces.push(new Piece(
                new Vector2(rawPiece.row, rawPiece.col),
                this.packService.getPieceType(rawPiece.pack_id, rawPiece.piece_type_id),
                rawPiece.color,
                rawPiece.direction,
            ));
        }

        for (const rawDecorator of parameters.decorators) {
            decorators.push(new Decorator(
                new Vector2(rawDecorator.row, rawDecorator.col),
                this.packService.getDecoratorType(rawDecorator.pack_id, rawDecorator.decorator_type_id),
            ));
        }

        for (const rawInfoElement of parameters.info_elements) {
            infoElements.push(new InfoElement(
                rawInfoElement.type,
                rawInfoElement.text,
                rawInfoElement.id,
            ));
        }

        for (const rawInventoryItem of parameters.inventory_items) {
            inventoryItems.push(new InventoryItem(
                rawInventoryItem.id,
                this.packService.getPieceType(rawInventoryItem.pack_id, rawInventoryItem.piece_type_id),
                rawInventoryItem.color,
                rawInventoryItem.direction,
                rawInventoryItem.label,
            ));
        }

        const winnerData = new WinnerData(parameters.winners.colors, parameters.winners.reason);

        this.handlers.updateGameData(parameters.id, new GameData(
            pieces,
            decorators,
            infoElements,
            inventoryItems,
            winnerData,
        ));
    }

    private showError(parameters: RawShowErrorParameters): void {
        this.snackBar.open(parameters.message, 'Ok', {
            duration: 5000,
            horizontalPosition: 'end',
            panelClass: 'error',
        });
    }

    private offerPlies(parameters: RawOfferPliesParameters): void {
        const from = new Vector2(parameters.from_row, parameters.from_col);
        const to = new Vector2(parameters.to_row, parameters.to_col);

        const plies: Ply[] = [];

        for (const rawPly of parameters.plies) {
            const actions: Action[] = [];

            for (const rawAction of rawPly.actions) {
                let actionFrom: Vector2 | null = null;
                let actionPieceType: PieceType | null = null;
                let actionColor: Color | null = null;
                let actionDirection: Direction | null = null;

                if (rawAction.type == 'Create') {
                    actionPieceType = this.packService.getPieceType(rawAction.piece.pack_id, rawAction.piece.piece_type_id);
                    actionColor = rawAction.piece.color;
                    actionDirection = rawAction.piece.direction;
                }
                else if (rawAction.type == 'Move') {
                    actionFrom = new Vector2(rawAction.from_pos_row, rawAction.from_pos_col);
                }

                actions.push(new Action(
                    rawAction.type,
                    new Vector2(rawAction.to_pos_row, rawAction.to_pos_col),
                    actionFrom,
                    actionPieceType,
                    actionColor,
                    actionDirection,
                ));
            }

            plies.push(new Ply(
                rawPly.name,
                actions,
            ))
        }

        this.handlers.offerPlies(from, to, plies);
    }

    connect(address: string): void {
        this.socket = webSocket(`ws://${address}`);

        this.socket.pipe(
            filter(message => message.hasOwnProperty('error'))
        ).subscribe(console.error);

        this.commands = this.socket.pipe(
            filter(message => message.hasOwnProperty('command') && message.hasOwnProperty('parameters')),
        );

        this.commands.subscribe(
            console.log,
            error => {
                if (error instanceof CloseEvent) {
                    alert('The server has closed.');
                } else {
                    alert('Cannot reach the server.');
                }
                this.router.navigate(['/']);
            },
        );

        this.getCommand('set_player').subscribe(this.setPlayer.bind(this));
        this.getCommand('focus_game').subscribe(this.focusGame.bind(this));
        this.getCommand('update_pack_data').subscribe(this.updatePackData.bind(this));
        this.getCommand('update_players').subscribe(this.updatePlayers.bind(this));
        this.getCommand('update_game_metadata').subscribe(this.updateGameMetadata.bind(this));
        this.getCommand('update_game_data').subscribe(this.updateGameData.bind(this));
        this.getCommand('show_error').subscribe(this.showError.bind(this));
        this.getCommand('offer_plies').subscribe(this.offerPlies.bind(this));
    }

    disconnect(): void {
        this.socket.complete();
    }

    // TODO: This could be a decorator.
    getCommand(command: string): Observable<unknown> {
        if (this.commands == undefined) {
            // Command was queried before connection was established. Forward user back to login.
            this.router.navigate(['/']);
            return;
        }

        return this.commands.pipe(
            filter(message => message['command'] == command),
            map(message => message['parameters']),
        );
    }

    login(displayName: string): void {
        this.run('login', {
            display_name: displayName,
        });
    }

    createGame(name: string, controller: Controller, options: {[key: string]: any}): void {
        this.run('create_game', {
            name: name,
            controller_pack_id: controller.pack.id,
            controller_id: controller.id,
            options: options,
        });
    }

    deleteGame(game: Game): void {
        this.run('delete_game', {
            game_id: game.id,
        });
    }

    showGame(game: Game): void {
        this.run('show_game', {
            game_id: game.id,
        });
    }

    joinGame(game: Game, color: Color): void {
        this.run('join_game', {
            game_id: game.id,
            color: color,
        });
    }

    leaveGame(game: Game): void {
        this.run('leave_game', {
            game_id: game.id,
        });
    }

    plies(game: Game, from: Vector2, to: Vector2): void {
        this.run('plies', {
            game_id: game.id,
            from_row: from.row,
            from_col: from.col,
            to_row: to.row,
            to_col: to.col,
        });
    }

    inventoryPlies(game: Game, inventoryItem: InventoryItem, to: Vector2): void {
        this.run('inventory_plies', {
            game_id: game.id,
            inventory_item_id: inventoryItem.id,
            to_row: to.row,
            to_col: to.col,
        });
    }

    submitPly(game: Game, from: Vector2, to: Vector2, ply: Ply): void {
        this.run('submit_ply', {
            game_id: game.id,
            from_row: from.row,
            from_col: from.col,
            to_row: to.row,
            to_col: to.col,
            ply: ply,
        });
    }

    clickButton(game: Game, button: InfoElement): void {
        this.run('click_button', {
            game_id: game.id,
            button_id: button.id,
        });
    }
}
