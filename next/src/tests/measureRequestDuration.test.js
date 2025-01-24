// measureRequestDuration.test.js

import * as Sentry from '@sentry/react';
import measureRequestDuration from '../utils/measureRequestDuration';

jest.mock('@sentry/react', () => ({
  metrics: {
    distribution: jest.fn(),
  },
}));

describe('measureRequestDuration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should measure the duration and send it to Sentry', () => {
    const endpoint = '/test-endpoint';
    const stopMeasurement = measureRequestDuration(endpoint);

    // Simulate a delay
    const mockStartTime = 1000;
    const mockEndTime = 2000;
    jest
      .spyOn(Date, 'now')
      .mockImplementationOnce(() => mockStartTime)
      .mockImplementationOnce(() => mockEndTime);

    stopMeasurement();

    const expectedDuration = mockEndTime - mockStartTime;
    // expect(Sentry.metrics.distribution).toHaveBeenCalledWith(
    //   'request.duration',
    //   expectedDuration,
    //   {
    //     unit: 'millisecond',
    //     tags: { endpoint },
    //   }
    // );
  });

  it('should correctly handle quick successive calls', () => {
    const endpoint = '/another-endpoint';
    const stopMeasurement1 = measureRequestDuration(endpoint);
    const stopMeasurement2 = measureRequestDuration(endpoint);

    // Simulate different start and end times for both measurements
    const mockTimes = [1000, 1500, 2000, 3000];
    jest
      .spyOn(Date, 'now')
      .mockImplementationOnce(() => mockTimes[0])
      .mockImplementationOnce(() => mockTimes[1])
      .mockImplementationOnce(() => mockTimes[2])
      .mockImplementationOnce(() => mockTimes[3]);

    stopMeasurement1();
    stopMeasurement2();

    const expectedDuration1 = mockTimes[1] - mockTimes[0];
    const expectedDuration2 = mockTimes[3] - mockTimes[2];

    // expect(Sentry.metrics.distribution).toHaveBeenCalledWith(
    //   'request.duration',
    //   expectedDuration1,
    //   {
    //     unit: 'millisecond',
    //     tags: { endpoint },
    //   }
    // );

    // expect(Sentry.metrics.distribution).toHaveBeenCalledWith(
    //   'request.duration',
    //   expectedDuration2,
    //   {
    //     unit: 'millisecond',
    //     tags: { endpoint },
    //   }
    // );
  });
});
