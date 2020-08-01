import {ChangeDetectorRef, EventEmitter, Injectable} from '@angular/core';
import {Controller, DecoratorType, PieceType} from "../pack/pack.service";
import {Color} from "../color/color.service";
import {Player} from "../player/player.service";
import {Identifiable, ItemService} from "../item-service";
import {ChatMessage} from "../chat/chat.service";

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

    toString(): string {
        return `Vector(${this.row}, ${this.col})`;
    }
}

export class Piece {
    constructor(
        public pos: Vector2,
        public type: PieceType,
        public color: Color,
        public direction: Direction,
    ) {}
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
        public pieces: Piece[],
        public decoratorLayers: {[layer: number]: Decorator[]},
        public infoElements: InfoElement[],
        public inventoryItems: InventoryItem[],
        public chatMessages: ChatMessage[],
        public winnerData?: WinnerData,
    ) {}
}

export class RenderData {
    firstDraw = true;

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

    // Temp until next refactor is done.
    scrollToBottom = new EventEmitter<Game>();

    private updateAvailableColors(): void {
        if (!this.selectedGame) {
            return;
        }

        this.availableColors = [...this.selectedGame.metadata.controller.colors];
        for (const color of Object.keys(this.selectedGame.metadata.players)) {
            this.availableColors.splice(this.availableColors.indexOf(Number(color)), 1);
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
                    new GameData([], [], [], [], []),
                    new RenderData(new Vector2(0, 0), Direction.NORTH, 80),
                )
            }
        }

        this.updateAvailableColors();
    }

    updateGameData(id: string, data: GameData): void {
        const game = this.items[id];

        game.data = data;

        // Temp until next refactor is done.
        setTimeout(() => {
            this.scrollToBottom.emit(game);
        }, 10);
    }

    updateDecorators(gameId: string, decoratorLayers: {[layer: number]: Decorator[]}): void {
        for (const [layer, decorators] of Object.entries(decoratorLayers)) {
            this.items[gameId].data.decoratorLayers[layer] = decorators;
        }

        this.updateBoard.emit();
    }
}
