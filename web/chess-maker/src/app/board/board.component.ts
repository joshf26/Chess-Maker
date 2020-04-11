import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';

@Component({
    selector: 'app-board',
    templateUrl: './board.component.html',
    styleUrls: ['./board.component.less']
})
export class BoardComponent implements OnInit {
    @ViewChild('canvas') public canvas: ElementRef<HTMLElement>;
    private context: CanvasRenderingContext2D;

    constructor() {}

    ngOnInit(): void {}

    ngAfterViewInit(): void {
        this.context = (<HTMLCanvasElement>this.canvas.nativeElement).getContext('2d');

        this.context.beginPath();
        this.context.rect(1, 1, 100, 100);
        this.context.stroke();
    }
}
