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
import {Decorator, InventoryItem, Piece, PieceMap, RenderData, Vector2} from "../../services/game/game.service";
import {MAX_ZOOM, MIN_ZOOM, PIECE_SIZE, ZOOM_FACTOR} from "../../constants";
import {InventorySurface} from "./surfaces/inventory-surface";
import {BoardSurface} from "./surfaces/board-surface";
import {PiecesSurface} from "./surfaces/pieces-surface";
import {MainSurface} from "./surfaces/main-surface";

export type Move = {
    from: Vector2,
    to: Vector2,
}

export type Place = {
    item: InventoryItem,
    to: Vector2,
}

export type DraggingData = {
    dragging: boolean,
    object?: Piece | InventoryItem,
    position?: Vector2,
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

    private mainSurface: MainSurface;
    private boardSurface: BoardSurface;
    private piecesSurface: PiecesSurface;
    private inventorySurface: InventorySurface;

    mousePositionX = 0;
    mousePositionY = 0;

    panning = false;
    panX: number;
    panY: number;
    draggingData: DraggingData = {
        dragging: false,
        object: undefined,
        position: undefined,
    };

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

    private updateBackgroundCanvases(): void {
        this.mainSurface.canvas.width = this.mainSurface.canvas.offsetWidth;
        this.mainSurface.canvas.height = this.mainSurface.canvas.offsetHeight;
        this.boardSurface.canvas.width = this.renderData.scale * this.boardSize.col;
        this.boardSurface.canvas.height = this.renderData.scale * this.boardSize.row;
        this.piecesSurface.canvas.width = this.renderData.scale * this.boardSize.col;
        this.piecesSurface.canvas.height = this.renderData.scale * this.boardSize.row;
        this.inventorySurface.canvas.width = PIECE_SIZE;

        // TODO: Ideally this should simply be set to this.canvas.offsetHeight. However, offsetHeight sometimes returns
        //       0 for no good reason. This should be investigated later.
        this.inventorySurface.canvas.height = Object.keys(this.inventory).length * PIECE_SIZE + 10;

        this.piecesSurface.draw(this.pieces, this.renderData);
        this.boardSurface.draw(this.decoratorLayers, this.boardSize, this.renderData);
        this.inventorySurface.draw(this.inventory, this.renderData.direction);
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
        this.mainSurface = new MainSurface(this.canvasElement.nativeElement);
        this.boardSurface = new BoardSurface();
        this.piecesSurface = new PiecesSurface();
        this.inventorySurface = new InventorySurface();

        this.updateAndCenter();

        fromEvent(window, 'resize').pipe(debounceTime(200)).subscribe(this.updateAndCenter.bind(this));
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (this.mainSurface) {
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
            (this.mainSurface.canvas.width) / 2,
            (this.mainSurface.canvas.height) / 2,
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

                if (event.offsetX > this.mainSurface.canvas.width - PIECE_SIZE && event.offsetY < this.inventory.length * PIECE_SIZE) {
                    // User clicked on an inventory item.
                    const inventoryItem = this.inventory[Math.floor(event.offsetY / PIECE_SIZE)];

                    this.draggingData.dragging = true;
                    this.draggingData.object = inventoryItem;

                    break;
                }

                const mouseTileX = Math.floor(this.mousePositionX);
                const mouseTileY = Math.floor(this.mousePositionY);

                for (const [pos, piece] of this.pieces.entries()) {
                    if (pos.row == mouseTileY && pos.col == mouseTileX) {
                        this.draggingData = {
                            dragging: true,
                            object: piece,
                            position: pos,
                        };

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
        if (this.draggingData.dragging) {
            this.snackBar.dismiss();

            const mouseTileX = Math.floor(this.mousePositionX);
            const mouseTileY = Math.floor(this.mousePositionY);

            this.draggingData.dragging = false;

            if (
                mouseTileX >= 0
                && mouseTileY >= 0
                && mouseTileY < this.boardSize.row
                && mouseTileX < this.boardSize.col
            ) {
                if (this.draggingData.object instanceof InventoryItem) {
                    this.place.emit({
                        item: this.draggingData.object,
                        to: new Vector2(mouseTileY, mouseTileX),
                    });
                }
                else if (this.draggingData.position.row != mouseTileY || this.draggingData.position.col != mouseTileX) {
                    this.move.emit({
                        from: this.draggingData.position,
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

        if (this.panning || this.draggingData.dragging) {
            this.draw();
        }
    }

    rawZoom(event: WheelEvent): boolean {
        this.zoom(event.deltaY, this.mousePositionX, this.mousePositionY);

        // Prevent the page from moving up or down.
        return false;
    }

    zoomCenter(delta: number): void {
        const [offsetX, offsetY] = this.rotateVector(this.mainSurface.canvas.width / 2, this.mainSurface.canvas.height / 2);
        this.zoom(
            delta,
            (offsetX - this.renderData.position.col) / this.renderData.scale,
            (offsetY - this.renderData.position.row) / this.renderData.scale,
        )
    }

    draw(): void {
        window.requestAnimationFrame(() => {
            this.mainSurface.draw(
                this.boardSurface,
                this.piecesSurface,
                this.inventorySurface,
                this.renderData,
                this.draggingData,
                this.mousePositionX,
                this.mousePositionY,
            );
        })
    }
}
