import {Injectable} from '@angular/core';

export const SVG_COLORS = [
    'white',
    'dimgrey',
    'red',
    'orange',
    'yellow',
    'green',
    'blue',
    'purple',
];

export enum Color {
    White,
    Black,
    Red,
    Orange,
    Yellow,
    Green,
    Blue,
    Purple,
}

@Injectable({
    providedIn: 'root'
})
export class ColorService {
    names = [
        'White',
        'Black',
        'Red',
        'Orange',
        'Yellow',
        'Green',
        'Blue',
        'Purple',
    ];

    constructor() {}
}
