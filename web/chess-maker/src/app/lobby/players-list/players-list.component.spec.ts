import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {PlayersListComponent} from './players.component';

describe('PlayersComponent', () => {
    let component: PlayersListComponent;
    let fixture: ComponentFixture<PlayersListComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [PlayersListComponent]
        }).compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(PlayersListComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
