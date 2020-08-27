import {ScaledScalingType, ScalingType} from "./scaling-type";

export abstract class Surface {
    protected context: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D;

    protected drawImage(
        image: HTMLImageElement,
        x: number,
        y: number,
        rotationAmount: number,
        scalingType: ScalingType,
    ) {
        this.context.translate(x, y);
        this.context.rotate(rotationAmount);

        if (scalingType instanceof ScaledScalingType) {
            this.context.drawImage(image, -scalingType.scale / 2, -scalingType.scale / 2, scalingType.scale, scalingType.scale);
        } else {
            this.context.drawImage(image, -image.width / 2, -image.height / 2, image.width, image.height);
        }

        this.context.rotate(-rotationAmount);
        this.context.translate(-x, -y);
    }

    abstract draw(...args): void;
}

export abstract class OnscreenSurface extends Surface {
    constructor(public canvas: HTMLCanvasElement) {
        super();

        this.context = canvas.getContext('2d');
    }
}

export abstract class OffscreenSurface extends Surface {
    canvas: OffscreenCanvas;

    constructor() {
        super();

        this.canvas = new OffscreenCanvas(0, 0);
        this.context = this.canvas.getContext('2d');
    }
}

