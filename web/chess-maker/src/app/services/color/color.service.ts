import {Injectable} from '@angular/core';

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
