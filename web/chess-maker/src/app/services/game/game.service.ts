import {EventEmitter, Injectable} from '@angular/core';
import {Controller, DecoratorType, PieceType} from "../pack/pack.service";
import {Color} from "../color/color.service";
import {Player} from "../player/player.service";
import {Identifiable, ItemService} from "../item-service";
import {ChatMessage} from "../chat/chat.service";
import {AudioService} from "../audio/audio.service";

export type NoDrawData = {[p: number]: {[p: number]: boolean}};

export enum Direction {
    NORTH,
    NORTH_EAST,
    EAST,
    SOUTH_EAST,
    SOUTH,
    SOUTH_WEST,
    WEST,
    NORTH_WEST,
}

export class Vector2 {
    constructor(
        public row: number,
        public col: number,
    ) {}

    plus(other: Vector2): Vector2 {
        return new Vector2(this.row + other.row, this.col + other.col);
    }

    minus(other: Vector2): Vector2 {
        return new Vector2(this.row - other.row, this.col - other.col);
    }

    dividedBy(amount: number): Vector2 {
        return new Vector2(this.row / amount, this.col / amount);
    }

    toString(): string {
        return `Vector(${this.row}, ${this.col})`;
    }
}

export class Piece {
    constructor(
        public type: PieceType,
        public color: Color,
        public direction: Direction,
    ) {}
}

export class PieceMap {
    private map: {[row: number]: {[col: number]: Piece}} = {};

    set(pos: Vector2, piece: Piece): void {
        if (!(pos.row in this.map)) {
            this.map[pos.row] = {};
        }

        this.map[pos.row][pos.col] = piece;
    }

    get(pos: Vector2): Piece {
        return this.map[pos.row][pos.col];
    }

    delete(pos: Vector2): void {
        delete this.map[pos.row][pos.col];
    }

    *entries(): Generator<[Vector2, Piece]> {
        for (const rawRow of Object.keys(this.map)) {
            const row = parseInt(rawRow);
            for (const [rawCol, piece] of Object.entries(this.map[row])) {
                const col = parseInt(rawCol);
                yield [new Vector2(row, col), piece];
            }
        }
    }
}

export class Decorator {
    constructor(
        public pos: Vector2,
        public type: DecoratorType,
    ) {}
}

export class InfoElement {
    constructor(
        public type: string,
        public text: string,
        public id?: string,
    ) {}
}

export class InventoryItem {
    constructor(
        public id: string,
        public type: PieceType,
        public color: Color,
        public direction: Direction,
        public label: string,
    ) {}
}

export class Action {
    constructor(
        public type: string,
        public toPos: Vector2,
        public fromPos?: Vector2,
        public pieceType?: PieceType,
        public color?: Color,
        public direction?: Direction,
    ) {}
}

export class Ply {
    constructor(
        public name: string,
        public actions: Action[],
    ) {}
}

export class WinnerData {
    constructor(
        public colors: number[],
        public reason: string,
    ) {}
}

export class GameMetadata {
    constructor(
        public displayName: string,
        public creator: Player,
        public controller: Controller,
        public players: {[color in Color]?: Player},
    ) {
    }
}

export class GameData {
    constructor(
        public pieces: PieceMap,
        public decoratorLayers: {[layer: number]: Decorator[]},
        public publicInfoElements: InfoElement[],
        public privateInfoElements: InfoElement[],
        public inventoryItems: InventoryItem[],
        public chatMessages: ChatMessage[],
        public winnerData?: WinnerData,
    ) {}
}

export class RenderData {
    firstDraw = true;
    noDrawData: NoDrawData = {};

    constructor(
        public position: Vector2,
        public direction: Direction,
        public scale: number,
    ) {}
}

export class Game implements Identifiable {
    constructor(
        public id: string,
        public metadata: GameMetadata,
        public data: GameData,
        public renderData: RenderData,
    ) {}

    playerCount(): number {
        return Object.keys(this.metadata.players).length;
    }

    playerInGame(player: Player): boolean {
        return !!Object.values(this.metadata.players).find(other_player => other_player.id == player.id);
    }
}

@Injectable({
    providedIn: 'root',
})
export class GameService extends ItemService<Game> {
    selectedGame?: Game;
    availableColors: number[];
    updateBoard = new EventEmitter();
    scrollToBottom = new EventEmitter<Game>();

    constructor(
        private audioService: AudioService,
    ) {
        super();
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

    private updateNoDraw(game: Game, decoratorLayers: {[layer: number]: Decorator[]}): void {
        if (1 in decoratorLayers) {
            game.renderData.noDrawData = {};

            for (const decorator of decoratorLayers[1]) {
                if (decorator.type.rawImage == 'NO DRAW') {
                    if (!(decorator.pos.row in game.renderData.noDrawData)) {
                        game.renderData.noDrawData[decorator.pos.row] = {};
                    }

                    game.renderData.noDrawData[decorator.pos.row][decorator.pos.col] = true;
                }
            }
        }
    }

    setSelectedGame(selectedGame: Game): void {
        this.selectedGame = selectedGame;
        this.updateAvailableColors();
    }

    updateGameMetadata(games: {[id: string]: GameMetadata}): void {
        for (const gameId in this.items) {
            if (!(gameId in games)) {
                if (this.selectedGame && this.selectedGame.id == gameId) {
                    this.selectedGame = undefined;
                }
                delete this.items[gameId];
            }
        }

        for (const [id, metadata] of Object.entries(games)) {
            if (id in this.items) {
                this.items[id].metadata = metadata;
            } else {
                this.items[id] = new Game(
                    id,
                    metadata,
                    new GameData(new PieceMap(), [], [], [], [], []),
                    new RenderData(new Vector2(0, 0), Direction.NORTH, 80),
                )
            }
        }

        this.updateAvailableColors();
    }

    updateGameData(id: string, data: GameData): void {
        const game = this.items[id];

        this.updateNoDraw(game, data.decoratorLayers);

        game.data = data;
    }

    updateDecorators(game: Game, decoratorLayers: {[layer: number]: Decorator[]}): void {
        for (const [layer, decorators] of Object.entries(decoratorLayers)) {
            game.data.decoratorLayers[layer] = decorators;
        }

        this.updateNoDraw(game, decoratorLayers);

        this.updateBoard.emit();
    }

    updateInfoElements(game: Game, infoElements: InfoElement[], isPublic: boolean): void {
        if (isPublic) {
            game.data.publicInfoElements = infoElements;
        } else {
            game.data.privateInfoElements = infoElements;
        }
    }

    updateInventoryItems(game: Game, inventoryItems: InventoryItem[]): void {
        game.data.inventoryItems = inventoryItems;

        this.updateBoard.emit();
    }

    applyPly(game: Game, ply: Ply): void {
        for (const action of ply.actions) {
            switch (action.type) {
                case 'move':
                    game.data.pieces.set(action.toPos, game.data.pieces.get(action.fromPos));
                    game.data.pieces.delete(action.fromPos);
                    break;
                case 'create':
                    game.data.pieces.set(action.toPos, new Piece(action.pieceType, action.color, action.direction));
                    break;
                case 'destroy':
                    game.data.pieces.delete(action.toPos);
                    break;
            }
        }

        this.audioService.playPly();
        this.updateBoard.emit();
    }

    updateWinners(game: Game, winnerData: WinnerData): void {
        game.data.winnerData = winnerData;
    }

    receiveGameChatMessage(game: Game, chatMessage: ChatMessage): void {
        game.data.chatMessages.push(chatMessage);

        this.scrollToBottom.emit(game);
    }
}
