import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';

const ODD_TILE_COLOR = '#A85738';
const EVEN_TILE_COLOR = '#F3C1A9';
const HIGHLIGHT_COLOR = '#FFFA00';
const ZOOM_FACTOR = 0.8;

interface Piece {
    color: string,
    positionX: number,
    positionY: number,
}

const PIECES: Piece[] = [
    {
        color: 'red',
        positionX: 5,
        positionY: 2,
    },
    {
        color: 'blue',
        positionX: 3,
        positionY: 6,
    },
];

@Component({
    selector: 'app-board',
    templateUrl: './board.component.html',
    styleUrls: ['./board.component.less']
})
export class BoardComponent implements OnInit {
    @ViewChild('canvas') private canvas_element: ElementRef<HTMLElement>;
    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;

    positionX = 0;
    positionY = 0;
    scale = 40;

    // Temp
    mousePositionX = 0;
    mousePositionY = 0;

    panning = false;
    dragging = false;
    draggingPiece?: Piece = null;
    panX: number;
    panY: number;

    constructor() {}

    ngOnInit(): void {}

    ngAfterViewInit(): void {
        this.canvas = <HTMLCanvasElement>this.canvas_element.nativeElement;
        this.context = this.canvas.getContext('2d');
        this.draw();
    }

    hideContextMenu(event: Event): void {
        event.preventDefault();
    }

    private updatePan(event: MouseEvent): void {
        this.panX = event.offsetX;
        this.panY = event.offsetY;
    }

    mouseDown(event: MouseEvent): void {
        switch (event.button) {
            case 0:
                // Prevent the user from accidentally selecting the canvas.
                event.preventDefault();

                const mouseTileX = Math.floor(this.mousePositionX);
                const mouseTileY = Math.floor(this.mousePositionY);

                for (const piece of PIECES) {
                    if (piece.positionX == mouseTileX && piece.positionY == mouseTileY) {
                        this.dragging = true;
                        this.draggingPiece = piece;

                        break;
                    }
                }

                break;
            case 2:
                this.panning = true;
                this.updatePan(event);
                break;
        }
    }

    mouseUp(): void {
        if (this.dragging) {
            const mouseTileX = Math.floor(this.mousePositionX);
            const mouseTileY = Math.floor(this.mousePositionY);

            this.dragging = false;

            this.draggingPiece.positionX = mouseTileX;
            this.draggingPiece.positionY = mouseTileY;
        }
        this.panning = false;
    }

    mouseMove(event: MouseEvent): void {
        this.mousePositionX = (event.offsetX - this.positionX) / this.scale;
        this.mousePositionY = (event.offsetY - this.positionY) / this.scale;

        if (this.panning) {
            const deltaX = this.panX - event.offsetX;
            const deltaY = this.panY - event.offsetY;

            this.positionX -= deltaX;
            this.positionY -= deltaY;

            this.updatePan(event);
        }

        this.draw();
    }

    zoom(event: WheelEvent): boolean {
        const factor = event.deltaY > 0 ? ZOOM_FACTOR : 1 / ZOOM_FACTOR;
        const deltaScale = (this.scale * factor) - this.scale;

        this.scale += deltaScale;
        this.positionX -= this.mousePositionX * deltaScale;
        this.positionY -= this.mousePositionY * deltaScale;

        this.draw();

        // Prevent the page from moving up or down.
        return false;
    }

    draw(): void {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const mouseTileX = Math.floor(this.mousePositionX);
        const mouseTileY = Math.floor(this.mousePositionY);
        const halfScale = this.scale / 2;

        for (let row = 0; row < 8; ++row) {
            for (let col = 0; col < 8; ++col) {
                if (mouseTileX == col && mouseTileY == row) {
                    this.context.fillStyle = HIGHLIGHT_COLOR;
                } else {
                    this.context.fillStyle = (col % 2 == row % 2) ? ODD_TILE_COLOR : EVEN_TILE_COLOR;
                }

                this.context.fillRect(col * this.scale + this.positionX, row * this.scale + this.positionY, this.scale, this.scale);

                for (const piece of PIECES) {
                    if (this.dragging && this.draggingPiece == piece) continue;

                    if (piece.positionX == col && piece.positionY == row) {
                        this.context.fillStyle = piece.color;
                        this.context.fillRect(
                            (col + 0.25) * this.scale + this.positionX,
                            (row + 0.25) * this.scale + this.positionY,
                            halfScale,
                            halfScale,
                        );
                    }
                }
            }
        }

        if (this.dragging) {
            this.context.fillStyle = this.draggingPiece.color;
            this.context.fillRect(
                (this.positionX + this.mousePositionX * this.scale) - halfScale / 2,
                (this.positionY + this.mousePositionY * this.scale) - halfScale / 2,
                halfScale,
                halfScale,
            );
        }
    }
}
