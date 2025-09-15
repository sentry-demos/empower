package com.sentrydemos.springboot;

import io.sentry.ISpan;
import io.sentry.Sentry;
import io.sentry.SpanStatus;

import java.util.function.Supplier;

/**
 * Custom functional interfaces that allow exceptions to be thrown.
 */
@FunctionalInterface
interface SupplierWithException<T> {
    T get() throws Exception;
}

@FunctionalInterface
interface RunnableWithException {
    void run() throws Exception;
}

/**
 * Utility class for creating and managing Sentry spans with consistent patterns.
 * Provides methods for creating spans with automatic error handling and resource management.
 */
public class SpanUtils {    
    
    /**
     * Creates a child span with automatic error handling and resource management.
     * Each individual span must be manually finished by calling finish() on it, otherwise spans will not appear in the transaction when there is an error before it finishes
     * https://docs.sentry.io/platforms/java/guides/spring-boot/tracing/instrumentation/custom-instrumentation/#add-more-spans-to-the-transaction:~:text=Keep%20in%20mind,spans%20have%20finished.
     * This version allows the operation to throw exceptions.
     * 
     * @param operation The operation name for the span
     * @param description The description of what the span represents
     * @param operationSupplier The operation to execute within the span
     * @return The result of the operation
     * @throws Exception if the operation throws an exception
     */
    public static <T> T executeWithSpan(String operation, String description, SupplierWithException<T> operationSupplier) throws Exception {
        ISpan span = Sentry.getSpan().startChild(operation, description);
        try {
            Sentry.logger().info("[springboot] - " + description + " started");
            T result = operationSupplier.get();
            Sentry.logger().info("[springboot] - " + description + " completed");
            return result;
        } catch (Exception e) {
            span.setThrowable(e);
            span.setStatus(SpanStatus.INTERNAL_ERROR);
            Sentry.logger().warn("[springboot] - " + description + " failed", e);
            throw e;
        } finally {
            span.finish();
        }
    }
    
    /**
     * Creates a child span for operations that don't return a value.
     * This version allows the operation to throw exceptions.
     * 
     * @param operation The operation name for the span
     * @param description The description of what the span represents
     * @param operationRunnable The operation to execute within the span
     * @throws Exception if the operation throws an exception
     */
    public static void executeWithSpan(String operation, String description, RunnableWithException operationRunnable) throws Exception {
        executeWithSpan(operation, description, () -> {
            operationRunnable.run();
            return null;
        });
    }
    
}
