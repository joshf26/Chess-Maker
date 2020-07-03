import {Injectable} from '@angular/core';
import {MatSidenav} from "@angular/material/sidenav";

@Injectable({
    providedIn: 'root',
})
export class SidebarService {
    private sidenav?: MatSidenav = null;

    registerSidenav(sidenav: MatSidenav): void {
        this.sidenav = sidenav;
    }

    isOpen(): boolean {
        if (!this.sidenav) return true;

        return this.sidenav.opened;
    }

    open(): void {
        if (!this.sidenav) return;

        this.sidenav.open();
    }

    close(): void {
        if (!this.sidenav) return;

        this.sidenav.close();
    }
}
