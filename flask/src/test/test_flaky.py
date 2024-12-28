import unittest
import random
import time

class FlakyTestExample(unittest.TestCase):
    def test_flaky_function(self):
        # Simulating a function that sometimes fails
        result = random.choice([False, False, False, False])
        
        # Adding delay to simulate randomness further
        time.sleep(random.uniform(0.1, 0.5))

        self.assertTrue(result, "The result was not True, indicating a flaky behavior")

if __name__ == "__main__":
    unittest.main()
