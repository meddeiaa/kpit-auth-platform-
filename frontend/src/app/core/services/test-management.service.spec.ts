import { TestBed } from '@angular/core/testing';

import { TestManagementService } from './test-management.service';

describe('TestManagementService', () => {
  let service: TestManagementService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TestManagementService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
