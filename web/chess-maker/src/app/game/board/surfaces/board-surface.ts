import {Decorator, RenderData, Vector2} from "../../../services/game/game.service";
import {EVEN_TILE_COLOR, ODD_TILE_COLOR} from "../../../constants";
import {ScalingType} from "./scaling-type";
import {OffscreenSurface} from "./surface";

export class BoardSurface extends OffscreenSurface {
    draw(decoratorLayers: {[layer: number]: Decorator[]}, boardSize: Vector2, renderData: RenderData): void {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        for (let row = 0; row < boardSize.row; ++row) {
            for (let col = 0; col < boardSize.col; ++col) {
                if (row in renderData.noDrawData && col in renderData.noDrawData[row]) continue;

                this.context.fillStyle = (col % 2 == row % 2) ? ODD_TILE_COLOR : EVEN_TILE_COLOR;
                this.context.fillRect(col * renderData.scale, row * renderData.scale, renderData.scale, renderData.scale);
            }
        }

        for (const [layer, decorators] of Object.entries(decoratorLayers)) {
            // TODO: Sort by layer.
            this.context.fillStyle = '#323232';
            for (const decorator of decorators) {
                if (decorator.type.rawImage != 'NO DRAW') {
                    this.drawImage(
                        decorator.type.image,
                        (decorator.pos.col + 0.5) * renderData.scale,
                        (decorator.pos.row + 0.5) * renderData.scale,
                        0,
                        ScalingType.scaled(renderData.scale),
                    )
                }
            }
        }
    }
}
