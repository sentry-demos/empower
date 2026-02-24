package com.sentrydemos.springboot.utils;

import io.sentry.ISpan;
import io.sentry.Sentry;
import io.sentry.SpanStatus;

import java.util.concurrent.Callable;

/**
 * Utility class for creating and managing Sentry spans with consistent patterns.
 * Provides methods for creating spans with automatic error handling and resource management.
 */
public class SpanUtils {

    /**
     * Creates a child span with automatic error handling and resource management.
     * Each individual span must be manually finished by calling finish() on it, otherwise spans will not appear in the transaction when there is an error before it finishes
     * https://docs.sentry.io/platforms/java/guides/spring-boot/tracing/instrumentation/custom-instrumentation/#add-more-spans-to-the-transaction:~:text=Keep%20in%20mind,spans%20have%20finished.
     * 
     * @param operation The operation name for the span
     * @param description The description of what the span represents
     * @param callable The operation to execute within the span
     * @return The result of the operation
     * @throws Exception if the operation throws an exception
     */
    public static <T> T executeWithSpan(String operation, String description, Callable<T> callable) throws Exception {
        ISpan span = Sentry.getSpan().startChild(operation, description);
        try {
            Sentry.logger().info(description + " started");
            T result = callable.call();
            Sentry.logger().info(description + " completed");
            return result;
        } catch (Exception e) {
            span.setThrowable(e);
            span.setStatus(SpanStatus.INTERNAL_ERROR);
            Sentry.logger().warn(description + " failed", e);
            throw e;
        } finally {
            span.finish();
        }
    }

    /**
     * Overloaded version for void operations - accepts RunnableWithException
     */
    public static void executeWithSpan(String operation, String description, RunnableWithException runnable) throws Exception {
        executeWithSpan(operation, description, () -> { runnable.run(); return null; });
    }

    @FunctionalInterface
    public interface RunnableWithException {
        void run() throws Exception;
    }

}