import {EventEmitter, Injectable} from '@angular/core';
import {webSocket, WebSocketSubject} from 'rxjs/webSocket';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {filter, map} from 'rxjs/operators';
import {Controller, PackService} from "../pack/pack.service";
import {Color} from "../color/color.service";
import {Game, GameService, InfoElement, InventoryItem, Ply, Vector2} from "../game/game.service";
import {PlayerService} from "../player/player.service";
import {ChatService} from "../chat/chat.service";
import {SetPlayerCommand} from "./commands/set-player-command";
import {UpdatePlayersCommand} from "./commands/update-players-command";
import {CommandService} from "./command.service";
import {UpdatePackDataCommand} from "./commands/update-pack-data-command";
import {UpdateGameMetadataCommand} from "./commands/update-game-metadata-command";
import {FocusGameCommand} from "./commands/focus-game-command";
import {UpdateGameDataCommand} from "./commands/update-game-data-command";
import {UpdateDecoratorsCommand} from "./commands/update-decorators-command";
import {UpdateInfoCommand} from "./commands/update-info-command";
import {UpdateInventoryCommand} from "./commands/update-inventory-command";
import {ApplyPlyCommand} from "./commands/apply-ply-command";
import {SetWinnersCommand} from "./commands/set-winners-command";
import {ReceiveGameChatCommand} from "./commands/receive-game-chat-command";
import {ReceiveServerChatCommand} from "./commands/receive-server-chat-command";
import {OfferPliesCommand} from "./commands/offer-plies-command";
import {ShowErrorCommand} from "./commands/show-error-command";

@Injectable({providedIn: 'root'})
export class ApiService {
    onForceDisconnect = new EventEmitter<string>();

    private socket?: WebSocketSubject<unknown>;
    private commands: Observable<unknown>;

    constructor(
        private router: Router,
        private gameService: GameService,
        private packService: PackService,
        private playerService: PlayerService,
        private chatService: ChatService,

        private commandService: CommandService,
        private setPlayerCommand: SetPlayerCommand,
        private focusGameCommand: FocusGameCommand,
        private updatePlayersCommand: UpdatePlayersCommand,
        private updatePackDataCommand: UpdatePackDataCommand,
        private updateGameMetadataCommand: UpdateGameMetadataCommand,
        private updateGameDataCommand: UpdateGameDataCommand,
        private updateDecoratorsCommand: UpdateDecoratorsCommand,
        private updateInfoCommand: UpdateInfoCommand,
        private updateInventoryCommand: UpdateInventoryCommand,
        private applyPlyCommand: ApplyPlyCommand,
        private setWinnersCommand: SetWinnersCommand,
        private receiveGameChatCommand: ReceiveGameChatCommand,
        private receiveServerChatCommand: ReceiveServerChatCommand,
        private offerPliesCommand: OfferPliesCommand,
        private showErrorCommand: ShowErrorCommand,
    ) {}

    private run(command: string, parameters: {[key: string]: any}): void {
        this.socket.next({
            command: command,
            parameters: parameters,
        });
    }

    connect(address: string, nickname: string): void {
        this.socket = webSocket(`ws://${address}/display_name=${nickname}`);

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
                    this.onForceDisconnect.emit('The server has closed.');
                } else {
                    this.onForceDisconnect.emit('Cannot reach the server.');
                }
                this.router.navigate(['/']);
            },
        );

        this.commandService.setSubjects({
            setPlayer: this.setPlayerCommand.subject,
            focusGame: this.focusGameCommand.subject,
            updatePlayers: this.updatePlayersCommand.subject,
            updatePackData: this.updatePackDataCommand.subject,
            updateGameMetadata: this.updateGameMetadataCommand.subject,
            updateGameData: this.updateGameDataCommand.subject,
            updateDecorators: this.updateDecoratorsCommand.subject,
            updateInfo: this.updateInfoCommand.subject,
            updateInventory: this.updateInventoryCommand.subject,
            applyPly: this.applyPlyCommand.subject,
            setWinners: this.setWinnersCommand.subject,
            receiveGameChat: this.receiveGameChatCommand.subject,
            receiveServerChat: this.receiveServerChatCommand.subject,
            offerPlies: this.offerPliesCommand.subject,
            showError: this.showErrorCommand.subject,
        });

        this.getCommand('set_player').subscribe(this.setPlayerCommand.run);
        this.getCommand('focus_game').subscribe(this.focusGameCommand.run);
        this.getCommand('update_pack_data').subscribe(this.updatePackDataCommand.run);
        this.getCommand('update_players').subscribe(this.updatePlayersCommand.run);
        this.getCommand('update_game_metadata').subscribe(this.updateGameMetadataCommand.run);
        this.getCommand('update_game_data').subscribe(this.updateGameDataCommand.run);
        this.getCommand('update_decorators').subscribe(this.updateDecoratorsCommand.run);
        this.getCommand('update_info_elements').subscribe(this.updateInfoCommand.run);
        this.getCommand('update_inventory_items').subscribe(this.updateInventoryCommand.run);
        this.getCommand('apply_ply').subscribe(this.applyPlyCommand.run);
        this.getCommand('update_winners').subscribe(this.setWinnersCommand.run);
        this.getCommand('receive_game_chat_message').subscribe(this.receiveGameChatCommand.run);
        this.getCommand('receive_server_chat_message').subscribe(this.receiveServerChatCommand.run);
        this.getCommand('offer_plies').subscribe(this.offerPliesCommand.run);
        this.getCommand('show_error').subscribe(this.showErrorCommand.run);
    }

    disconnect(): void {
        this.socket.complete();
        this.socket = null;
    }

    isConnected(): boolean {
        return !!this.socket;
    }

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
            ply: {
                name: ply.name,
                actions: ply.actions.map(action => {
                    const result = {
                        type: action.type,
                        to_pos_row: action.toPos.row,
                        to_pos_col: action.toPos.col,
                    };

                    if (action.fromPos) {
                        result['from_pos_row'] = action.fromPos.row;
                        result['from_pos_col'] = action.fromPos.col;
                    }

                    if (action.pieceType) {
                        result['piece'] = {
                            pack_id: action.pieceType.pack.id,
                            piece_type_id: action.pieceType.id,
                            color: action.color,
                            direction: action.direction,
                        };
                    }

                    return result;
                }),
            },
        });
    }

    clickButton(game: Game, button: InfoElement): void {
        this.run('click_button', {
            game_id: game.id,
            button_id: button.id,
        });
    }

    sendChatMessage(text: string, game?: Game): void {
        this.run('send_chat_message', {
            text: text,
            game_id: game ? game.id : 'server',
        });
    }
}
