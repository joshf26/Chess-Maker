import {PieceMap, RenderData} from "../../../services/game/game.service";
import {ScalingType} from "./scaling-type";
import {OffscreenSurface} from "./surface";

export class PiecesSurface extends OffscreenSurface {
    draw(pieces: PieceMap, renderData: RenderData): void {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (const [pos, piece] of pieces.entries()) {
            this.drawImage(
                piece.type.images[piece.color],
                (pos.col + 0.5) * renderData.scale,
                (pos.row + 0.5) * renderData.scale,
                piece.direction * Math.PI / 4,
                ScalingType.scaled(renderData.scale),
            );
        }
    }
}
