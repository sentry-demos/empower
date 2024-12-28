describe("Flaky Test Example", () => {
    test("sometimes passes, sometimes fails", () => {
      // Simulating a function that sometimes returns true and sometimes false
      const result = Math.random() > 0.0;
      
      // Adding a small delay to make it even flakier
      return new Promise((resolve) => {
        setTimeout(() => {
          expect(result).toBe(true);
          resolve();
        }, Math.random() * 500);
      });
    });
  });
  