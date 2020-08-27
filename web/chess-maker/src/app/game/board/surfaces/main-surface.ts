import {OffscreenSurface, OnscreenSurface} from "./surface";
import {ScalingType} from "./scaling-type";
import {PIECE_SIZE} from "../../../constants";
import {RenderData} from "../../../services/game/game.service";
import {DraggingData} from "../board.component";

export class MainSurface extends OnscreenSurface {
    draw(
        boardSurface: OffscreenSurface,
        piecesSurface: OffscreenSurface,
        inventorySurface: OffscreenSurface,
        renderData: RenderData,
        draggingData: DraggingData,
        mousePositionX: number,
        mousePositionY: number,
    ): void {
        this.context.fillStyle = '#323232';
        this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.context.rotate(renderData.direction * Math.PI / 4);

        this.context.drawImage(boardSurface.canvas, renderData.position.col, renderData.position.row);
        this.context.drawImage(piecesSurface.canvas, renderData.position.col, renderData.position.row);

        if (draggingData.dragging) {
            this.drawImage(
                draggingData.object.type.images[draggingData.object.color],
                renderData.position.col + mousePositionX * renderData.scale,
                renderData.position.row + mousePositionY * renderData.scale,
                draggingData.object.direction * Math.PI / 4,
                ScalingType.scaled(renderData.scale),
            );
        }

        this.context.rotate(-renderData.direction * Math.PI / 4);
        this.context.drawImage(inventorySurface.canvas, this.canvas.width - PIECE_SIZE, 0);
    }
}
