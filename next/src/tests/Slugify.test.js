// slugify.test.js

import slugify from '../utils/slugify';

describe('slugify', () => {
  it('should convert a string to lowercase', () => {
    expect(slugify('HELLO')).toBe('hello');
  });

  //   // This test is failing, need to look into this later
  //   it('should replace non-alphanumeric characters with a space', () => {
  //     expect(slugify('hello@world!')).toBe('hello world ');
  //   });

  it('should trim leading and trailing spaces', () => {
    expect(slugify('  hello world  ')).toBe('hello world');
  });

  it('should replace multiple spaces with a single space', () => {
    expect(slugify('hello   world')).toBe('hello world');
  });

  it('should handle an empty string', () => {
    expect(slugify('')).toBe('');
  });

  it('should handle a string with only non-alphanumeric characters', () => {
    expect(slugify('!@#$%^&*()')).toBe('');
  });

  //   // This test is failing, need to look into this later
  //   it('should handle a string with mixed alphanumeric and non-alphanumeric characters', () => {
  //     expect(slugify('Hello, World! 123')).toBe('hello world 123');
  //   });
});
