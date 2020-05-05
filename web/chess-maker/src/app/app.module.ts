import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {FormsModule} from '@angular/forms';
import {BoardComponent} from './board/board.component';
import {MenuComponent} from './menu/menu.component';
import {LobbyComponent} from './lobby/lobby.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import {MatChipsModule} from '@angular/material/chips';
import {MatBadgeModule} from '@angular/material/badge';

@NgModule({
    declarations: [
        AppComponent,
        BoardComponent,
        MenuComponent,
        LobbyComponent,
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        FormsModule,
        BrowserAnimationsModule,
        MatSidenavModule,
        MatCardModule,
        MatButtonModule,
        MatChipsModule,
        MatBadgeModule,
    ],
    providers: [],
    bootstrap: [AppComponent],
})
export class AppModule {}
