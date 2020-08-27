import {OffscreenSurface} from "./surface";
import {Direction, InventoryItem} from "../../../services/game/game.service";
import {PIECE_SIZE} from "../../../constants";
import {ScalingType} from "./scaling-type";

export class InventorySurface extends OffscreenSurface {
    draw(inventory: InventoryItem[], direction: Direction): void {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.context.font = '15px Arial';
        this.context.fillStyle = 'white';

        for (const [index, piece] of inventory.entries()) {
            const image = piece.type.images[piece.color];
            const rotation = ((piece.direction + direction) % 8) * Math.PI / 4;
            this.drawImage(
                image,
                PIECE_SIZE / 2,
                index * PIECE_SIZE + PIECE_SIZE / 2,
                rotation,
                ScalingType.fixed());
            this.context.fillText(piece.label, 0, (index + 1) * PIECE_SIZE);
        }
    }
}
