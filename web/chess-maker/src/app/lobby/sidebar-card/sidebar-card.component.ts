import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';

@Component({
    selector: 'app-sidebar-card',
    templateUrl: './sidebar-card.component.html',
    styleUrls: ['./sidebar-card.component.less'],
})
export class SidebarCardComponent implements OnInit {
    @Input() header: string;
    @Output('onNew') onNew = new EventEmitter();

    constructor() {}

    ngOnInit(): void {}
}
