import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Game, InfoElement} from "../../services/game/game.service";
import {DomSanitizer} from "@angular/platform-browser";

@Component({
    selector: 'app-info-box',
    templateUrl: './info-box.component.html',
    styleUrls: ['./info-box.component.less'],
})
export class InfoBoxComponent implements OnInit {
    @Input() infoElements: InfoElement[];
    @Input() disableButtons: boolean;
    @Input() isPublic: boolean;
    @Output() buttonClick = new EventEmitter<InfoElement>();

    constructor(public sanitizer: DomSanitizer) {}

    ngOnInit(): void {}
}
