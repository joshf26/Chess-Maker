import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {FormsModule} from '@angular/forms';
import { BoardComponent } from './board/board.component';

@NgModule({
    declarations: [
        AppComponent,
        BoardComponent,
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        FormsModule, // Temp for ngModel
    ],
    providers: [],
    bootstrap: [AppComponent],
})
export class AppModule {}
