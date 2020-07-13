import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {FormsModule} from '@angular/forms';
import {MenuComponent} from './menu/menu.component';
import {LobbyComponent} from './lobby/lobby.component';
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
import {MatTabsModule} from "@angular/material/tabs";
import {MatTooltipModule} from "@angular/material/tooltip";
import {MatCheckboxModule} from "@angular/material/checkbox";
import {MatSnackBarModule} from "@angular/material/snack-bar";
import {GameComponent} from './game/game.component';
import {BoardComponent} from "./game/board/board.component";
import {GamesListComponent} from './lobby/games-list/games-list.component';
import {PlayersListComponent} from "./lobby/players-list/players-list.component";
import {CreateGameDialog} from "./lobby/create-game-dialog/create-game-dialog.component";
import {SelectPlyDialog} from "./lobby/select-ply-dialog/select-ply-dialog.component";
import {MatExpansionModule} from "@angular/material/expansion";
import {SidebarCardComponent} from './lobby/sidebar-card/sidebar-card.component';
import {MatProgressSpinnerModule} from "@angular/material/progress-spinner";
import {ChatComponent} from "./lobby/chat/chat.component";
import { ChatBoxComponent } from './lobby/chat/chat-box/chat-box.component';

@NgModule({
    declarations: [
        AppComponent,
        BoardComponent,
        MenuComponent,
        LobbyComponent,
        CreateGameDialog,
        SelectPlyDialog,
        PlayersListComponent,
        GameComponent,
        BoardComponent,
        GamesListComponent,
        SidebarCardComponent,
        ChatComponent,
        ChatBoxComponent,
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
        MatExpansionModule,
        MatProgressSpinnerModule,
    ],
    providers: [],
    bootstrap: [AppComponent],
})
export class AppModule {
}
