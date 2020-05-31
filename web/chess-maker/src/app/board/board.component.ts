import {Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {PackDataService} from '../services/pieces/pack-data.service';
import {GameMetaData} from '../lobby/lobby.component';
import {DomSanitizer} from '@angular/platform-browser';
import {MatSidenav} from "@angular/material/sidenav";
import {fromEvent} from "rxjs";
import {debounceTime} from "rxjs/operators";

const EVEN_TILE_COLOR = '#A85738';
const ODD_TILE_COLOR = '#F3C1A9';
const MIN_ZOOM = 10;
const MAX_ZOOM = 300;
const ZOOM_FACTOR = 0.8;
const PIECE_SIZE = 45;

interface Piece {
    row: number,
    col: number,
    pack: string,
    piece: string,
    color: number,
    direction: number,
}

interface InventoryPiece {
    pack: string,
    name: string,
    color: number,
    direction: number,
    quantity: number,
}

export interface WinnerData {
    colors: number[],
    reason: string,
}

interface GameData {
    id: string,
    pieces: Piece[],
    info: InfoElement[],
    inventory: InventoryPiece[],
    winners?: WinnerData,
}

interface InfoElement {
    type: string,
    text: string,
    id?: string,
}

@Component({
    selector: 'app-board',
    templateUrl: './board.component.html',
    styleUrls: ['./board.component.less']
})
export class BoardComponent implements OnInit {
    @ViewChild('canvas') private canvasElement: ElementRef<HTMLElement>;
    @Input('game') game: GameMetaData;
    @Input('gameId') private gameId: string;
    @Input('notify') private notify: (gameId: string) => void;  // TODO: Maybe this should be an @Output?
    @Input('sidenav') sidenav: MatSidenav;
    @Output('winner') private winner = new EventEmitter<WinnerData>();

    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;
    private boardCanvas: OffscreenCanvas;
    private boardContext: OffscreenCanvasRenderingContext2D;
    private piecesCanvas: OffscreenCanvas;
    private piecesContext: OffscreenCanvasRenderingContext2D;
    private inventoryCanvas: OffscreenCanvas;
    private inventoryContext: OffscreenCanvasRenderingContext2D;

    positionX = 0;
    positionY = 0;
    scale = 40;

    mousePositionX = 0;
    mousePositionY = 0;

    boardSizeRows = 8;
    boardSizeCols = 8;

    panning = false;
    dragging = false;
    draggingPiece?: Piece = undefined;
    panX: number;
    panY: number;
    angle = 0;

    pieces: Piece[] = [];
    infoElements: InfoElement[] = [];
    inventoryPieces: InventoryPiece[] = [];

    constructor(
        private api: ApiService,
        public packDataService: PackDataService,
        public sanitizer: DomSanitizer,
    ) {
        api.getCommand('full_game_data').subscribe(this.gameDataHandler.bind(this));
    }

    ngOnInit(): void {}

    ngAfterViewInit(): void {
        this.canvas = <HTMLCanvasElement>this.canvasElement.nativeElement;
        this.context = this.canvas.getContext('2d');
        this.boardCanvas = new OffscreenCanvas(0, 0);
        this.boardContext = this.boardCanvas.getContext('2d');
        this.piecesCanvas = new OffscreenCanvas(0, 0);
        this.piecesContext = this.piecesCanvas.getContext('2d');
        this.inventoryCanvas = new OffscreenCanvas(PIECE_SIZE, 0);
        this.inventoryContext = this.inventoryCanvas.getContext('2d');
        this.updateBackgroundCanvases();
        this.centerBoard();

        fromEvent(window, 'resize').pipe(debounceTime(200)).subscribe(() => {
            this.updateBackgroundCanvases();
            this.centerBoard();
        });
    }

    private rotateVector(x: number, y: number): number[] {
        const rad_angle = -this.angle * Math.PI / 4;

        return [
            x * Math.cos(rad_angle) - y * Math.sin(rad_angle),
            y * Math.cos(rad_angle) + x * Math.sin(rad_angle),
        ];
    }

    onResize(): void {
        this.updateBackgroundCanvases();
        this.centerBoard();
    }

    updateBoardSize(): void {
        const board = this.packDataService.boardTypes[this.game.pack][this.game.board];
        this.boardSizeRows = board.rows;
        this.boardSizeCols = board.cols;

        this.centerBoard();
    }

    gameDataHandler(gameData: GameData): void {
        if (gameData.id == this.gameId) {
            this.pieces = gameData.pieces;
            this.infoElements = gameData.info;
            this.inventoryPieces = gameData.inventory;

            this.winner.emit(gameData.winners);

            this.updateBackgroundCanvases();
            this.draw();
        } else {
            this.notify(gameData.id);
        }
    }

    centerBoard(): void {
        const [x, y] = this.rotateVector(
            (this.canvas.width) / 2,
            (this.canvas.height) / 2,
        )

        this.positionX = x - this.boardSizeCols * this.scale / 2;
        this.positionY = y - this.boardSizeRows * this.scale / 2;

        this.draw();
    }

    rotate(): void {
        this.angle = (this.angle + 1) % 8;
        this.updateBackgroundCanvases();
        this.centerBoard();
    }

    leaveGame(): void {
        this.api.run('leave_game', {game_id: this.gameId});
    }

    updateBackgroundCanvases(): void {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        this.boardCanvas.width = this.scale * this.boardSizeRows;
        this.boardCanvas.height = this.scale * this.boardSizeCols;
        this.piecesCanvas.width = this.scale * this.boardSizeRows;
        this.piecesCanvas.height = this.scale * this.boardSizeCols;
        this.inventoryCanvas.height = this.canvas.offsetHeight;

        // Pieces
        this.piecesContext.clearRect(0, 0, this.boardCanvas.width, this.boardCanvas.height);
        for (const piece of this.pieces) {
            this.drawImage(
                this.piecesContext,
                this.packDataService.pieceTypes[piece.pack][piece.piece][piece.color].image,
                (piece.col + 0.5) * this.scale,
                (piece.row + 0.5) * this.scale,
                piece.direction * Math.PI / 4,
            );
        }

        // Board
        this.boardContext.clearRect(0, 0, this.boardCanvas.width, this.boardCanvas.height);
        for (let row = 0; row < this.boardSizeRows; ++row) {
            for (let col = 0; col < this.boardSizeCols; ++col) {
                this.boardContext.fillStyle = (col % 2 == row % 2) ? ODD_TILE_COLOR : EVEN_TILE_COLOR;
                this.boardContext.fillRect(col * this.scale, row * this.scale, this.scale, this.scale);
            }
        }

        // Inventory
        this.inventoryContext.clearRect(0, 0, this.inventoryCanvas.width, this.inventoryCanvas.height);
        for (const [index, piece] of this.inventoryPieces.entries()) {
            const image = this.packDataService.pieceTypes[piece.pack][piece.name][piece.color].image;
            const rotation = ((piece.direction + this.angle) % 8) * Math.PI / 4;
            this.drawImage(this.inventoryContext, image, PIECE_SIZE / 2, index * PIECE_SIZE + PIECE_SIZE / 2, rotation, true);
        }
    }

    hideContextMenu(event: Event): void {
        event.preventDefault();
    }

    private updatePan(offsetX: number, offsetY: number): void {
        this.panX = offsetX;
        this.panY = offsetY;
    }

    mouseDown(event: MouseEvent): void {
        switch (event.button) {
            case 0:
                // Prevent the user from accidentally selecting the canvas.
                event.preventDefault();

                if (!this.game) {
                    break;
                }

                if (event.offsetX > this.canvas.width - PIECE_SIZE && event.offsetY < this.inventoryPieces.length * PIECE_SIZE) {
                    const piece = this.inventoryPieces[Math.floor(event.offsetY / PIECE_SIZE)];

                    this.dragging = true;
                    this.draggingPiece = {
                        row: -1,
                        col: -1,
                        color: piece.color,
                        pack: piece.pack,
                        piece: piece.name,
                        direction: piece.direction
                    };

                    break;
                }

                const mouseTileX = Math.floor(this.mousePositionX);
                const mouseTileY = Math.floor(this.mousePositionY);

                for (const piece of this.pieces) {
                    if (piece.row == mouseTileY && piece.col == mouseTileX) {
                        this.dragging = true;
                        this.draggingPiece = piece;

                        break;
                    }
                }

                break;
            case 2:
                this.panning = true;

                const [offsetX, offsetY] = this.rotateVector(event.offsetX, event.offsetY);
                this.updatePan(offsetX, offsetY);

                break;
        }
    }

    mouseUp(): void {
        if (this.dragging) {
            const mouseTileX = Math.floor(this.mousePositionX);
            const mouseTileY = Math.floor(this.mousePositionY);

            this.dragging = false;

            if (
                mouseTileX >= 0
                && mouseTileY >= 0
                && mouseTileY < this.boardSizeRows
                && mouseTileX < this.boardSizeCols
            ) {
                if (this.draggingPiece.row == -1 && this.draggingPiece.col == -1) {
                    // The piece came from the inventory.
                    // TODO: Use a different system for this.

                    this.api.run('inventory_plies', {
                        'game_id': this.gameId,
                        'pack_name': this.draggingPiece.pack,
                        'piece_name': this.draggingPiece.piece,
                        'piece_color': this.draggingPiece.color,
                        'piece_direction': this.draggingPiece.direction,
                        'to_row': mouseTileY,
                        'to_col': mouseTileX,
                    })
                }
                else if (this.draggingPiece.row != mouseTileY || this.draggingPiece.col != mouseTileX) {
                    this.api.run('plies', {
                        'game_id': this.gameId,
                        'from_row': this.draggingPiece.row,
                        'from_col': this.draggingPiece.col,
                        'to_row': mouseTileY,
                        'to_col': mouseTileX,
                    })
                }
            }

            this.draw();
        }

        this.panning = false;
    }

    mouseMove(event: MouseEvent): void {
        const [offsetX, offsetY] = this.rotateVector(event.offsetX, event.offsetY);

        this.mousePositionX = (offsetX - this.positionX) / this.scale;
        this.mousePositionY = (offsetY - this.positionY) / this.scale;

        if (this.panning) {
            const deltaX = this.panX - offsetX;
            const deltaY = this.panY - offsetY;

            this.positionX -= deltaX;
            this.positionY -= deltaY;

            this.updatePan(offsetX, offsetY);
        }

        this.draw();
    }

    zoom(event: WheelEvent): boolean {
        const factor = event.deltaY > 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR;
        const deltaScale = (this.scale * factor) - this.scale;

        const newScale = this.scale + deltaScale;
        if (newScale < MIN_ZOOM || newScale > MAX_ZOOM) return false;

        this.scale += deltaScale;
        this.positionX -= this.mousePositionX * deltaScale;
        this.positionY -= this.mousePositionY * deltaScale;

        this.updateBackgroundCanvases();
        this.draw();

        // Prevent the page from moving up or down.
        return false;
    }

    draw(): void {
        this.context.fillStyle = '#303030';
        this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.context.rotate(this.angle * Math.PI / 4);

        this.context.drawImage(this.boardCanvas, this.positionX, this.positionY);
        this.context.drawImage(this.piecesCanvas, this.positionX, this.positionY);

        if (this.dragging) {
            this.drawImage(
                this.context,
                this.packDataService.pieceTypes[this.draggingPiece.pack][this.draggingPiece.piece][this.draggingPiece.color].image,
                this.positionX + this.mousePositionX * this.scale,
                this.positionY + this.mousePositionY * this.scale,
                this.draggingPiece.direction * Math.PI / 4,
            );
        }

        this.context.rotate(-this.angle * Math.PI / 4);

        this.context.drawImage(this.inventoryCanvas, this.canvas.width - PIECE_SIZE, 0);
    }

    private drawImage(
        context: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
        image: HTMLImageElement,
        x: number,
        y: number,
        rotationAmount: number,
        fixed: boolean = false,
    ) {
        context.translate(x, y);
        context.rotate(rotationAmount);

        if (fixed) {
            context.drawImage(image, -image.width / 2, -image.height / 2, image.width, image.height);
        } else {
            context.drawImage(image, -this.scale / 2, -this.scale / 2, this.scale, this.scale);
        }

        context.rotate(-rotationAmount);
        context.translate(-x, -y);
    }

    click_button(id: string): void {
        this.api.run('click_button', {
            'game_id': this.gameId,
            'button_id': id,
        });
    }
}
