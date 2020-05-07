import {Injectable} from '@angular/core';

// A piece type is accessed using [pack][piece][color].
export type PieceTypes = {[key: string]: {[key: string]: {image: HTMLImageElement}[]}};

// A board type is accessed using [pack][board].
export type BoardTypes = {[key: string]: {[key: string]: {rows: number, cols: number}}};

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
export class PackDataService {
    pieceTypes: PieceTypes = {};
    boardTypes: BoardTypes = {};
    boardNames: {pack: string, name: string}[] = [];

    updatePackData(rawPackData: any): void {
        for (const [pack, packData] of Object.entries(rawPackData)) {
            this.pieceTypes[pack] = {};

            for (const [piece, pieceData] of Object.entries(packData['pieces'])) {
                this.pieceTypes[pack][piece] = [];

                for (let color = 0; color < 8; ++color) {
                    const image = new Image();
                    // TODO: Instead of replacing the "white", it should replace use a special keyword.
                    image.src = `data:image/svg+xml,${pieceData['image'].replace(/white/g, SVG_COLORS[color])}`;

                    this.pieceTypes[pack][piece][color] = {image: image};
                }
            }

            this.boardTypes[pack] = packData['boards'];
        }

        this.updateBoardNames();
    }

    updateBoardNames(): void {
        this.boardNames = [];

        for (const [pack, boards] of Object.entries(this.boardTypes)) {
            for (const board of Object.keys(boards)) {
                this.boardNames.push({
                    pack: pack,
                    name: board,
                });
            }
        }
    }
}
