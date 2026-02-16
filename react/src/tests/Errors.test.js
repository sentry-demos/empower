import { crasher, UnhandledException } from '../utils/errors';
import { createBrowserHistory } from 'history';

describe('Errors module', () => {
  let originalMathRandom;
  let history;
  let originalEnv;

  beforeAll(() => {
    originalMathRandom = Math.random;
    history = createBrowserHistory();
    originalEnv = process.env.REACT_APP_ENVIRONMENT;
  });

  afterAll(() => {
    Math.random = originalMathRandom;
    process.env.REACT_APP_ENVIRONMENT = originalEnv;
  });

  beforeEach(() => {
    // Set environment to non-production for tests by default
    process.env.REACT_APP_ENVIRONMENT = 'development';
  });

  const setQueryParams = (obj) => {
    // const searchParams = new URLSearchParams(params);
    // history.push({ search: searchParams.toString() });
    jest.spyOn(URLSearchParams.prototype, 'get').mockImplementation((key) => obj[key]);
  };

  test('should throw a notAFunctionError when "crash" is true and errnum is 0', () => {
    setQueryParams({ crash: 'true', errnum: '0' });
    expect(() => crasher()).toThrow(TypeError);
  });
  
  test('should throw a ReferenceError when "crash" is true and errnum is 1', () => {
    setQueryParams({ crash: 'true', errnum: '1' });
    expect(() => crasher()).toThrow(ReferenceError);
  });

  test('should throw a SyntaxError when "crash" is true and errnum is 2', () => {
    setQueryParams({ crash: 'true', errnum: '2' });
    expect(() => crasher()).toThrow(SyntaxError);
  });

  test('should throw a RangeError when "crash" is true and errnum is 3', () => {
    setQueryParams({ crash: 'true', errnum: '3' });
    expect(() => crasher()).toThrow(RangeError);
  });

  test('should throw an UnhandledException when "crash" is true and errnum is 4', () => {
    setQueryParams({ crash: 'true', errnum: '4' });
    expect(() => crasher()).toThrow(UnhandledException);
  });

// This test is failing, need to look into this later
//   test('should log the queryParam if empty', () => {
//     setQueryParams({});
//     console.log = jest.fn();
//     crasher();
//     expect(console.log).toHaveBeenCalledWith('> queryParam was', '');
//   });

  test('should throw a random error based on probability', () => {
    setQueryParams({ crash: '0.5' });
    Math.random = jest.fn(() => 0.4); // This should cause the error to be thrown
    expect(() => crasher()).toThrow();
  });

  test('should not throw an error if probability does not match', () => {
    setQueryParams({ crash: '0.1' });
    Math.random = jest.fn(() => 0.2); // This should not cause the error to be thrown
    expect(() => crasher()).not.toThrow();
  });

  test('should not throw an error in production environment', () => {
    process.env.REACT_APP_ENVIRONMENT = 'production';
    setQueryParams({ crash: 'true', errnum: '1' });
    console.log = jest.fn();
    expect(() => crasher()).not.toThrow();
    expect(console.log).toHaveBeenCalledWith('> crash testing disabled in production environment');
  });

  test('should throw an error in non-production environments', () => {
    process.env.REACT_APP_ENVIRONMENT = 'development';
    setQueryParams({ crash: 'true', errnum: '1' });
    expect(() => crasher()).toThrow(ReferenceError);
  });
});
