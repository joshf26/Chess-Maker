import {Injectable} from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class PreferencesService {
    constructor() {
        if (!this.address) this.address = '34.68.92.191:1137';
        if (!this.displayName) this.displayName = 'Player';
    }

    get address() {return localStorage.getItem('address');}
    get displayName() {return localStorage.getItem('displayName');}

    set address(value: string) {localStorage.setItem('address', value);}
    set displayName(value: string) {localStorage.setItem('displayName', value);}
}
