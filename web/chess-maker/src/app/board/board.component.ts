import {Component, ElementRef, Input, OnInit, Output, ViewChild} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {PackDataService} from '../services/pieces/pack-data.service';
import {GameMetaData} from '../lobby/lobby.component';

const ODD_TILE_COLOR = '#A85738';
const EVEN_TILE_COLOR = '#F3C1A9';
const HIGHLIGHT_COLOR = '#FFFA00';
const ZOOM_FACTOR = 0.8;

interface Piece {
    row: number,
    col: number,
    pack: string,
    piece: string,
    color: number,
    direction: number,
}

interface GameData {
    id: string,
    tiles: Piece[],
}

@Component({
    selector: 'app-board',
    templateUrl: './board.component.html',
    styleUrls: ['./board.component.less']
})
export class BoardComponent implements OnInit {
    @ViewChild('canvas') private canvasElement: ElementRef<HTMLElement>;
    @Input('game') private game: GameMetaData;
    @Input('gameId') private gameId: string;
    @Input('notify') private notify: (gameId: string) => void;  // TODO: Maybe this should be an @Output?

    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;
    private boardCanvas: OffscreenCanvas;
    private boardContext: OffscreenCanvasRenderingContext2D;
    private piecesCanvas: OffscreenCanvas;
    private piecesContext: OffscreenCanvasRenderingContext2D;

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

    constructor(
        private api: ApiService,
        private packDataService: PackDataService,
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
        this.updateBackgroundCanvases();
        this.centerBoard();
    }

    private rotateVector(x: number, y: number): number[] {
        const rad_angle = -this.angle * Math.PI / 4;

        return [
            x * Math.cos(rad_angle) - y * Math.sin(rad_angle),
            y * Math.cos(rad_angle) + x * Math.sin(rad_angle),
        ];
    }

    updateBoardSize(): void {
        const board = this.packDataService.boardTypes[this.game.pack][this.game.board];
        this.boardSizeRows = board.rows;
        this.boardSizeCols = board.cols;

        this.centerBoard();
    }

    gameDataHandler(gameData: GameData): void {
        if (gameData.id == this.gameId) {
            this.pieces = gameData.tiles;
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
        this.centerBoard();
    }

    updateBackgroundCanvases(): void {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        this.boardCanvas.width = this.scale * this.boardSizeRows;
        this.boardCanvas.height = this.scale * this.boardSizeCols;
        this.piecesCanvas.width = this.scale * this.boardSizeRows;
        this.piecesCanvas.height = this.scale * this.boardSizeCols;

        this.piecesContext.clearRect(0, 0, this.boardCanvas.width, this.boardCanvas.height);
        for (const piece of this.pieces) {
            this.drawImage(
                this.piecesContext,
                this.packDataService.pieceTypes[piece.pack][piece.piece][piece.color == 8 ? 0 : piece.color].image,
                (piece.col + 0.5) * this.scale,
                (piece.row + 0.5) * this.scale,
                piece.direction * Math.PI / 4,
            );
        }

        this.boardContext.clearRect(0, 0, this.boardCanvas.width, this.boardCanvas.height);
        for (let row = 0; row < this.boardSizeRows; ++row) {
            for (let col = 0; col < this.boardSizeCols; ++col) {
                this.boardContext.fillStyle = (col % 2 == row % 2) ? ODD_TILE_COLOR : EVEN_TILE_COLOR;
                this.boardContext.fillRect(col * this.scale, row * this.scale, this.scale, this.scale);
            }
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

                const mouseTileX = Math.floor(this.mousePositionX);
                const mouseTileY = Math.floor(this.mousePositionY);

                for (const piece of this.pieces) {
                    if (piece.row == mouseTileY && piece.col == mouseTileX) {
                        if (this.game && piece.color == this.game.playing_as) {
                            this.dragging = true;
                            this.draggingPiece = piece;
                        }

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

            if (this.draggingPiece.row != mouseTileY || this.draggingPiece.col != mouseTileX) {
                this.api.run('get_plies', {
                    'game_id': this.gameId,
                    'from_row': this.draggingPiece.row,
                    'from_col': this.draggingPiece.col,
                    'to_row': mouseTileY,
                    'to_col': mouseTileX,
                })
            }
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
    }

    private drawImage(
        context: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
        image: HTMLImageElement,
        x: number,
        y: number,
        rotationAmount: number,
    ) {
        context.translate(x, y);
        context.rotate(rotationAmount);

        context.drawImage(image, -this.scale / 2, -this.scale / 2, this.scale, this.scale);

        context.rotate(-rotationAmount);
        context.translate(-x, -y);
    }
}
