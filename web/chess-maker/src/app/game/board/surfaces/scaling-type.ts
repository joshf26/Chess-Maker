export abstract class ScalingType {
    static scaled(scale: number): ScalingType { return new ScaledScalingType(scale); }
    static fixed(): ScalingType { return new FixedScalingType(); }
}

export class ScaledScalingType extends ScalingType {
    constructor(public scale: number) {super();}
}

export class FixedScalingType extends ScalingType {}
