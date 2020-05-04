import {Injectable} from '@angular/core';

// A piece type is accessed using [pack][piece][color].
export type PieceTypes = {[key: string]: {[key: string]: {image: HTMLImageElement}[]}};

const SVG_COLORS = [
    'white',
    'dimgrey',
    'red',
    'orange',
    'yellow',
    'green',
    'blue',
    'purple',
]

@Injectable({
    providedIn: 'root'
})
export class PiecesService {
    pieceTypes: PieceTypes = {};

    updatePieceTypes(rawPieceTypes: any) {
        for (const [pack, packData] of Object.entries(rawPieceTypes)) {
            this.pieceTypes[pack] = {};

            for (const [piece, pieceData] of Object.entries(packData)) {
                this.pieceTypes[pack][piece] = [];

                for (let color = 0; color < 8; ++color) {
                    const image = new Image();
                    // TODO: Instead of replacing the "white", it should replace use a special keyword.
                    image.src = `data:image/svg+xml,${pieceData.image.replace(/white/g, SVG_COLORS[color])}`;

                    this.pieceTypes[pack][piece][color] = {image: image};
                }
            }
        }
    }
}
