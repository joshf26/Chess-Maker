import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {MenuComponent} from './menu/menu.component';
import {LobbyComponent} from './lobby/lobby.component';


const routes: Routes = [
    {path: '', component: MenuComponent},
    {path: 'lobby', component: LobbyComponent},
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule {}
