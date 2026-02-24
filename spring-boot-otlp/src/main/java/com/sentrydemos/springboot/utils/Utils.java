package com.sentrydemos.springboot.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Utils {
    
    private static final Logger logger = LoggerFactory.getLogger(Utils.class);
    
    /**
     * @param n the position in the Fibonacci sequence
     * @return the nth Fibonacci number
     */
    public static int getIterator(int n) {
        if (n < 0) {
            logger.warn("[logback] - Incorrect input: negative number provided to getIterator");
            return 0;
        } else if (n == 0) {
            return 0;
        } else if (n == 1 || n == 2) {
            return 1;
        } else {
            return getIterator(n - 1) + getIterator(n - 2);
        }
    }
    
}
