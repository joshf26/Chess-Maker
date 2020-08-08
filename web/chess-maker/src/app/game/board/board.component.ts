import {
    Component,
    ElementRef,
    EventEmitter,
    Input,
    OnChanges,
    OnInit,
    Output,
    SimpleChanges,
    ViewChild
} from '@angular/core';
import {fromEvent} from "rxjs";
import {debounceTime} from "rxjs/operators";
import {MatSnackBar} from "@angular/material/snack-bar";
import {
    Direction,
    Vector2,
    Decorator,
    InventoryItem,
    Piece,
    RenderData,
    PieceMap
} from "../../services/game/game.service";

const EVEN_TILE_COLOR = '#A85738';
const ODD_TILE_COLOR = '#F3C1A9';
const MIN_ZOOM = 10;
const MAX_ZOOM = 300;
const ZOOM_FACTOR = 0.8;
const PIECE_SIZE = 45;

export type Move = {
    from: Vector2,
    to: Vector2,
}

export type Place = {
    item: InventoryItem,
    to: Vector2,
}

class Surface {
    public canvas: OffscreenCanvas;
    public context: OffscreenCanvasRenderingContext2D;

    constructor() {
        this.canvas = new OffscreenCanvas(0, 0);
        this.context = this.canvas.getContext('2d');
    }
}

@Component({
    selector: 'app-board',
    templateUrl: './board.component.html',
    styleUrls: ['./board.component.less']
})
export class BoardComponent implements OnInit, OnChanges {
    @Input() private pieces: PieceMap;
    @Input() private decoratorLayers: {[layer: number]: Decorator[]};
    @Input() private inventory: InventoryItem[];
    @Input() private boardSize: Vector2;
    @Input() private renderData: RenderData;
    @Output() private move = new EventEmitter<Move>();
    @Output() private place = new EventEmitter<Place>();
    @ViewChild('canvas') private canvasElement: ElementRef<HTMLCanvasElement>;

    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;
    private boardSurface: Surface;
    private piecesSurface: Surface;
    private inventorySurface: Surface;

    mousePositionX = 0;
    mousePositionY = 0;

    panning = false;
    dragging = false;
    draggingPiece?: Piece | InventoryItem;
    draggingPiecePos?: Vector2;
    panX: number;
    panY: number;

    constructor(private snackBar: MatSnackBar) {}

    private rotateVector(x: number, y: number): number[] {
        const radAngle = -this.renderData.direction * Math.PI / 4;

        return [
            x * Math.cos(radAngle) - y * Math.sin(radAngle),
            y * Math.cos(radAngle) + x * Math.sin(radAngle),
        ];
    }

    private updatePan(offsetX: number, offsetY: number): void {
        this.panX = offsetX;
        this.panY = offsetY;
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
            context.drawImage(image, -this.renderData.scale / 2, -this.renderData.scale / 2, this.renderData.scale, this.renderData.scale);
        }

        context.rotate(-rotationAmount);
        context.translate(-x, -y);
    }

    private updateBackgroundCanvases(): void {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        this.boardSurface.canvas.width = this.renderData.scale * this.boardSize.col;
        this.boardSurface.canvas.height = this.renderData.scale * this.boardSize.row;
        this.piecesSurface.canvas.width = this.renderData.scale * this.boardSize.col;
        this.piecesSurface.canvas.height = this.renderData.scale * this.boardSize.row;
        this.inventorySurface.canvas.width = PIECE_SIZE;

        // TODO: Ideally this should simply be set to this.canvas.offsetHeight. However, offsetHeight sometimes returns
        //       0 for no good reason. This should be investigated later.
        this.inventorySurface.canvas.height = Object.keys(this.inventory).length * PIECE_SIZE + 10;

        // Pieces
        this.piecesSurface.context.clearRect(0, 0, this.piecesSurface.canvas.width, this.piecesSurface.canvas.height);
        for (const [pos, piece] of this.pieces.entries()) {
            this.drawImage(
                this.piecesSurface.context,
                piece.type.images[piece.color],
                (pos.col + 0.5) * this.renderData.scale,
                (pos.row + 0.5) * this.renderData.scale,
                piece.direction * Math.PI / 4,
            );
        }

        // Board
        this.boardSurface.context.clearRect(0, 0, this.boardSurface.canvas.width, this.boardSurface.canvas.height);
        for (let row = 0; row < this.boardSize.row; ++row) {
            for (let col = 0; col < this.boardSize.col; ++col) {
                if (row in this.renderData.noDrawData && col in this.renderData.noDrawData[row]) continue;

                this.boardSurface.context.fillStyle = (col % 2 == row % 2) ? ODD_TILE_COLOR : EVEN_TILE_COLOR;
                this.boardSurface.context.fillRect(col * this.renderData.scale, row * this.renderData.scale, this.renderData.scale, this.renderData.scale);
            }
        }

        for (const [layer, decorators] of Object.entries(this.decoratorLayers)) {
            // TODO: Sort by layer.
            this.boardSurface.context.fillStyle = '#323232';
            for (const decorator of decorators) {
                if (decorator.type.rawImage != 'NO DRAW') {
                    this.drawImage(
                        this.boardSurface.context,
                        decorator.type.image,
                        (decorator.pos.col + 0.5) * this.renderData.scale,
                        (decorator.pos.row + 0.5) * this.renderData.scale,
                        0,
                    )
                }
            }
        }

        // Inventory
        this.inventorySurface.context.clearRect(0, 0, this.inventorySurface.canvas.width, this.inventorySurface.canvas.height);
        this.inventorySurface.context.font = '15px Arial';
        this.inventorySurface.context.fillStyle = 'white';
        for (const [index, piece] of this.inventory.entries()) {
            const image = piece.type.images[piece.color];
            const rotation = ((piece.direction + this.renderData.direction) % 8) * Math.PI / 4;
            this.drawImage(this.inventorySurface.context, image, PIECE_SIZE / 2, index * PIECE_SIZE + PIECE_SIZE / 2, rotation, true);
            this.inventorySurface.context.fillText(piece.label, 0, (index + 1) * PIECE_SIZE);
        }
    }

    private zoom(delta: number, centerX: number, centerY: number): void {
        const factor = delta > 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR;
        const deltaScale = (this.renderData.scale * factor) - this.renderData.scale;

        const newScale = this.renderData.scale + deltaScale;
        if (newScale < MIN_ZOOM || newScale > MAX_ZOOM) return;

        this.renderData.scale += deltaScale;
        this.renderData.position.col -= centerX * deltaScale;
        this.renderData.position.row -= centerY * deltaScale;

        this.updateBackgroundCanvases();
        this.draw();
    }

    ngOnInit(): void {}

    ngAfterViewInit(): void {
        this.canvas = this.canvasElement.nativeElement;
        this.context = this.canvas.getContext('2d');
        this.boardSurface = new Surface();
        this.piecesSurface = new Surface();
        this.inventorySurface = new Surface();

        this.updateAndCenter();

        fromEvent(window, 'resize').pipe(debounceTime(200)).subscribe(this.updateAndCenter.bind(this));
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.canvas) {
            this.updateBackgroundCanvases();

            if (this.renderData.firstDraw) {
                this.centerBoard();
                this.renderData.firstDraw = false;
            }

            this.draw();
        }
    }

    centerBoard(): void {
        const [x, y] = this.rotateVector(
            (this.canvas.width) / 2,
            (this.canvas.height) / 2,
        );

        this.renderData.position.col = x - this.boardSize.col * this.renderData.scale / 2;
        this.renderData.position.row = y - this.boardSize.row * this.renderData.scale / 2;

        this.draw();
    }

    updateAndCenter() {
        this.updateBackgroundCanvases();
        this.centerBoard();
    }

    hideContextMenu(event: Event): void {
        event.preventDefault();
    }

    mouseDown(event: MouseEvent): void {
        switch (event.button) {
            case 0: // Left click.
                // Prevent the user from accidentally selecting the canvas.
                event.preventDefault();

                if (event.offsetX > this.canvas.width - PIECE_SIZE && event.offsetY < this.inventory.length * PIECE_SIZE) {
                    // User clicked on an inventory item.
                    const inventoryItem = this.inventory[Math.floor(event.offsetY / PIECE_SIZE)];

                    this.dragging = true;
                    this.draggingPiece = inventoryItem;

                    break;
                }

                const mouseTileX = Math.floor(this.mousePositionX);
                const mouseTileY = Math.floor(this.mousePositionY);

                for (const [pos, piece] of this.pieces.entries()) {
                    if (pos.row == mouseTileY && pos.col == mouseTileX) {
                        this.dragging = true;
                        this.draggingPiece = piece;
                        this.draggingPiecePos = pos;

                        break;
                    }
                }

                break;
            case 2: // Right click.
                this.panning = true;

                const [offsetX, offsetY] = this.rotateVector(event.offsetX, event.offsetY);
                this.updatePan(offsetX, offsetY);

                break;
        }
    }

    mouseUp(): void {
        if (this.dragging) {
            this.snackBar.dismiss();

            const mouseTileX = Math.floor(this.mousePositionX);
            const mouseTileY = Math.floor(this.mousePositionY);

            this.dragging = false;

            if (
                mouseTileX >= 0
                && mouseTileY >= 0
                && mouseTileY < this.boardSize.row
                && mouseTileX < this.boardSize.col
            ) {
                if (this.draggingPiece instanceof InventoryItem) {
                    this.place.emit({
                        item: this.draggingPiece,
                        to: new Vector2(mouseTileY, mouseTileX),
                    });
                }
                else if (this.draggingPiecePos.row != mouseTileY || this.draggingPiecePos.col != mouseTileX) {
                    this.move.emit({
                        from: this.draggingPiecePos,
                        to: new Vector2(mouseTileY, mouseTileX),
                    });
                }
            }

            this.draw();
        }

        this.panning = false;
    }

    mouseMove(event: MouseEvent): void {
        const [offsetX, offsetY] = this.rotateVector(event.offsetX, event.offsetY);

        this.mousePositionX = (offsetX - this.renderData.position.col) / this.renderData.scale;
        this.mousePositionY = (offsetY - this.renderData.position.row) / this.renderData.scale;

        if (this.panning) {
            const deltaX = this.panX - offsetX;
            const deltaY = this.panY - offsetY;

            this.renderData.position.col -= deltaX;
            this.renderData.position.row -= deltaY;

            this.updatePan(offsetX, offsetY);
        }

        if (this.panning || this.dragging) {
            this.draw();
        }
    }

    rawZoom(event: WheelEvent): boolean {
        this.zoom(event.deltaY, this.mousePositionX, this.mousePositionY);

        // Prevent the page from moving up or down.
        return false;
    }

    zoomCenter(delta: number): void {
        const [offsetX, offsetY] = this.rotateVector(this.canvas.width / 2, this.canvas.height / 2);
        this.zoom(
            delta,
            (offsetX - this.renderData.position.col) / this.renderData.scale,
            (offsetY - this.renderData.position.row) / this.renderData.scale,
        )
    }

    draw(): void {
        window.requestAnimationFrame(() => {
            this.context.fillStyle = '#323232';
            this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

            this.context.rotate(this.renderData.direction * Math.PI / 4);

            this.context.drawImage(this.boardSurface.canvas, this.renderData.position.col, this.renderData.position.row);
            this.context.drawImage(this.piecesSurface.canvas, this.renderData.position.col, this.renderData.position.row);

            if (this.dragging) {
                this.drawImage(
                    this.context,
                    this.draggingPiece.type.images[this.draggingPiece.color],
                    this.renderData.position.col + this.mousePositionX * this.renderData.scale,
                    this.renderData.position.row + this.mousePositionY * this.renderData.scale,
                    this.draggingPiece.direction * Math.PI / 4,
                );
            }

            this.context.rotate(-this.renderData.direction * Math.PI / 4);
            this.context.drawImage(this.inventorySurface.canvas, this.canvas.width - PIECE_SIZE, 0);
        })
    }
}
