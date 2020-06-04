import {TestBed} from '@angular/core/testing';

import {PackDataService} from './pack-data.service';

describe('PackDataService', () => {
    let service: PackDataService;

    beforeEach(() => {
        TestBed.configureTestingModule({});
        service = TestBed.inject(PackDataService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
