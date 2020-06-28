import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {FormsModule} from '@angular/forms';
import {MenuComponent} from './menu/menu.component';
import {LobbyComponent, SelectPlyDialog} from './lobby/lobby.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import {MatChipsModule} from '@angular/material/chips';
import {MatBadgeModule} from '@angular/material/badge';
import {MatDialogModule} from '@angular/material/dialog';
import {MatSelectModule} from '@angular/material/select';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';
import {MatListModule} from '@angular/material/list';
import {PlayersComponent} from './players/players.component';
import {MatTabsModule} from "@angular/material/tabs";
import {MatTooltipModule} from "@angular/material/tooltip";
import {CreateGameDialog} from "./lobby/create-game-dialog.component";
import {MatCheckboxModule} from "@angular/material/checkbox";
import {MatSnackBarModule} from "@angular/material/snack-bar";
import {GameComponent} from './game/game.component';
import {BoardComponent} from "./game/board/board.component";

@NgModule({
    declarations: [
        AppComponent,
        BoardComponent,
        MenuComponent,
        LobbyComponent,
        CreateGameDialog,
        SelectPlyDialog,
        PlayersComponent,
        GameComponent,
        BoardComponent,
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
        MatDialogModule,
        MatSelectModule,
        MatSnackBarModule,
        MatInputModule,
        MatIconModule,
        MatListModule,
        MatTabsModule,
        MatTooltipModule,
        MatCheckboxModule,
    ],
    providers: [],
    bootstrap: [AppComponent],
})
export class AppModule {
}
