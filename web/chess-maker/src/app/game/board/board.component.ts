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
import {Direction, Vector2, Decorator, InventoryItem, Piece} from "../../services/game/game.service";

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
    @Input('pieces') private pieces: Piece[];
    @Input('decorators') private decorators: Decorator[];
    @Input('inventory') private inventory: InventoryItem[];
    @Input('boardSize') private boardSize: Vector2;
    @Input('direction') private direction: Direction;
    @Output('move') private move = new EventEmitter<Move>();
    @Output('place') private place = new EventEmitter<Place>();
    @ViewChild('canvas') private canvasElement: ElementRef<HTMLElement>;

    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;
    private boardSurface: Surface;
    private piecesSurface: Surface;
    private inventorySurface: Surface;

    positionX = 0;
    positionY = 0;
    scale = 40;

    mousePositionX = 0;
    mousePositionY = 0;

    panning = false;
    dragging = false;
    draggingPiece?: Piece | InventoryItem;
    panX: number;
    panY: number;

    constructor(private snackBar: MatSnackBar) {}

    private rotateVector(x: number, y: number): number[] {
        const radAngle = -this.direction * Math.PI / 4;

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
            context.drawImage(image, -this.scale / 2, -this.scale / 2, this.scale, this.scale);
        }

        context.rotate(-rotationAmount);
        context.translate(-x, -y);
    }

    private centerBoard(): void {
        const [x, y] = this.rotateVector(
            (this.canvas.width) / 2,
            (this.canvas.height) / 2,
        )

        this.positionX = x - this.boardSize.col * this.scale / 2;
        this.positionY = y - this.boardSize.row * this.scale / 2;

        this.draw();
    }

    private updateBackgroundCanvases(): void {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
        this.boardSurface.canvas.width = this.scale * this.boardSize.col;
        this.boardSurface.canvas.height = this.scale * this.boardSize.row;
        this.piecesSurface.canvas.width = this.scale * this.boardSize.col;
        this.piecesSurface.canvas.height = this.scale * this.boardSize.row;
        this.inventorySurface.canvas.width = PIECE_SIZE;
        this.inventorySurface.canvas.height = this.canvas.offsetHeight;

        // Pieces
        this.piecesSurface.context.clearRect(0, 0, this.piecesSurface.canvas.width, this.piecesSurface.canvas.height);
        for (const piece of this.pieces) {
            this.drawImage(
                this.piecesSurface.context,
                piece.type.images[piece.color],
                (piece.pos.col + 0.5) * this.scale,
                (piece.pos.row + 0.5) * this.scale,
                piece.direction * Math.PI / 4,
            );
        }

        // Board
        this.boardSurface.context.clearRect(0, 0, this.boardSurface.canvas.width, this.boardSurface.canvas.height);
        for (let row = 0; row < this.boardSize.row; ++row) {
            for (let col = 0; col < this.boardSize.col; ++col) {
                this.boardSurface.context.fillStyle = (col % 2 == row % 2) ? ODD_TILE_COLOR : EVEN_TILE_COLOR;
                this.boardSurface.context.fillRect(col * this.scale, row * this.scale, this.scale, this.scale);
            }
        }

        for (const decorator of this.decorators) {
            if (decorator.type.rawImage != 'NO DRAW') { // TODO: Work on this.
                this.drawImage(
                    this.boardSurface.context,
                    decorator.type.image,
                    (decorator.pos.col + 0.5) * this.scale,
                    (decorator.pos.row + 0.5) * this.scale,
                    0,
                )
            }
        }

        // Inventory
        this.inventorySurface.context.clearRect(0, 0, this.inventorySurface.canvas.width, this.inventorySurface.canvas.height);
        this.inventorySurface.context.font = '15px Arial';
        this.inventorySurface.context.fillStyle = 'white';
        for (const [index, piece] of this.inventory.entries()) {
            const image = piece.type.images[piece.color];
            const rotation = ((piece.direction + this.direction) % 8) * Math.PI / 4;
            this.drawImage(this.inventorySurface.context, image, PIECE_SIZE / 2, index * PIECE_SIZE + PIECE_SIZE / 2, rotation, true);
            this.inventorySurface.context.fillText(piece.label, 0, (index + 1) * PIECE_SIZE);
        }
    }

    private zoom(delta: number, centerX: number, centerY: number): void {
        const factor = delta > 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR;
        const deltaScale = (this.scale * factor) - this.scale;

        const newScale = this.scale + deltaScale;
        if (newScale < MIN_ZOOM || newScale > MAX_ZOOM) return;

        this.scale += deltaScale;
        this.positionX -= centerX * deltaScale;
        this.positionY -= centerY * deltaScale;

        this.updateBackgroundCanvases();
        this.draw();
    }

    ngOnInit(): void {}

    ngAfterViewInit(): void {
        this.canvas = <HTMLCanvasElement>this.canvasElement.nativeElement;
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

            if ('direction' in changes) {
                this.centerBoard();
            } else {
                this.draw();
            }
        }
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

                for (const piece of this.pieces) {
                    if (piece.pos.row == mouseTileY && piece.pos.col == mouseTileX) {
                        this.dragging = true;
                        this.draggingPiece = piece;

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
                else if (this.draggingPiece.pos.row != mouseTileY || this.draggingPiece.pos.col != mouseTileX) {
                    this.move.emit({
                        from: this.draggingPiece.pos,
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

        this.mousePositionX = (offsetX - this.positionX) / this.scale;
        this.mousePositionY = (offsetY - this.positionY) / this.scale;

        if (this.panning) {
            const deltaX = this.panX - offsetX;
            const deltaY = this.panY - offsetY;

            this.positionX -= deltaX;
            this.positionY -= deltaY;

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
            (offsetX - this.positionX) / this.scale,
            (offsetY - this.positionY) / this.scale,
        )
    }

    draw(): void {
        window.requestAnimationFrame(() => {
            this.context.fillStyle = '#323232';
            this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

            this.context.rotate(this.direction * Math.PI / 4);

            this.context.drawImage(this.boardSurface.canvas, this.positionX, this.positionY);
            this.context.drawImage(this.piecesSurface.canvas, this.positionX, this.positionY);

            if (this.dragging) {
                this.drawImage(
                    this.context,
                    this.draggingPiece.type.images[this.draggingPiece.color],
                    this.positionX + this.mousePositionX * this.scale,
                    this.positionY + this.mousePositionY * this.scale,
                    this.draggingPiece.direction * Math.PI / 4,
                );
            }

            this.context.rotate(-this.direction * Math.PI / 4);
            this.context.drawImage(this.inventorySurface.canvas, this.canvas.width - PIECE_SIZE, 0);
        })
    }
}
