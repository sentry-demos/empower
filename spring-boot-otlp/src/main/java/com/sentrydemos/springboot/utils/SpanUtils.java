package com.sentrydemos.springboot.utils;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

import io.sentry.Sentry;

import java.util.concurrent.Callable;

/**
 * Utility class for creating and managing OpenTelemetry spans with consistent patterns.
 * Provides methods for creating spans with automatic error handling and resource management.
 * 
 * Spans created here are automatically sent to Sentry via the sentry-opentelemetry-agent.
 */
public class SpanUtils {

    private static final String INSTRUMENTATION_NAME = "com.sentrydemos.springboot";

    private static Tracer getTracer() {
        return GlobalOpenTelemetry.getTracer(INSTRUMENTATION_NAME);
    }

    /**
     * Creates a child span with automatic error handling and resource management.
     * The span is automatically linked to the current trace context.
     * 
     * @param operation The operation name for the span
     * @param description The description of what the span represents
     * @param callable The operation to execute within the span
     * @return The result of the operation
     * @throws Exception if the operation throws an exception
     */
    public static <T> T executeWithSpan(String operation, String description, Callable<T> callable) throws Exception {
        Span span = getTracer()
            .spanBuilder(operation)
            .setSpanKind(SpanKind.INTERNAL)
            .setAttribute("description", description)
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            Sentry.logger().info(description + " started");
            T result = callable.call();
            Sentry.logger().info(description + " completed");
            return result;
        } catch (Exception e) {
            span.setStatus(StatusCode.ERROR, e.getMessage());
            span.recordException(e);
            Sentry.logger().warn(description + " failed", e);
            throw e;
        } finally {
            span.end();
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
