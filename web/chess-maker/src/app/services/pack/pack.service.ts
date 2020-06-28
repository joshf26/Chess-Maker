import {Injectable} from '@angular/core';
import {Vector2} from "../game/game.service";
import {Color, SVG_COLORS} from "../color/color.service";
import {Identifiable, ItemService} from "../item-service";

function getImage(rawImage: string, color: Color = Color.White): HTMLImageElement {
    const image = new Image();
    image.src = `data:image/svg+xml,${rawImage.replace(/white/g, SVG_COLORS[color])}`;
    return image;
}

export class Pack implements Identifiable {
    constructor(
        public id: string,
        public displayName: string,
        public controllers: {[id: string]: Controller},
        public pieceTypes: {[id: string]: PieceType},
        public decoratorTypes: {[id: string]: DecoratorType},
    ) {}
}

export class PieceType implements Identifiable {
    images: {[color in Color]?: HTMLImageElement} = {};

    constructor(
        public id: string,
        public pack: Pack,
        public rawImage: string,
    ) {
        for (let color = 0; color < 8; ++color) {
            this.images[color] = getImage(rawImage, color);
        }
    }
}

export class DecoratorType implements Identifiable {
    image: HTMLImageElement;

    constructor(
        public id: string,
        public pack: Pack,
        public rawImage: string,
    ) {
        this.image = getImage(rawImage);
    }
}

export class Controller implements Identifiable {
    constructor(
        public id: string,
        public displayName: string,
        public pack: Pack,
        public boardSize: Vector2,
        public colors: Color[],
        public options: {[key: string]: any},
    ) {}
}

@Injectable({
    providedIn: 'root',
})
export class PackService extends ItemService<Pack> {
    updatePackData(packs: {[key: string]: Pack}): void {
        this.items = packs;
    }

    getController(packId: string, controllerId: string): Controller {
        return this.items[packId].controllers[controllerId];
    }

    getPieceType(packId: string, pieceTypeId: string): PieceType {
        return this.items[packId].pieceTypes[pieceTypeId];
    }

    getDecoratorType(packId: string, decoratorTypeId: string): DecoratorType {
        return this.items[packId].decoratorTypes[decoratorTypeId];
    }
}
