import * as Sentry from '@sentry/react';

function getTag(tag) {
    return Sentry.getCurrentScope()._tags[tag]
}

function itemsInCart(cart) {
    return Object.values(cart).reduce((a, b) => a + b, 0)
}

// Returns a captureContext callback (the standard second arg to
// Sentry.captureException) that pins the event to the page it's called from.
// In a SPA a subsequent navigate() changes window.location synchronously while
// Sentry enriches events asynchronously (httpContext sets request.url from
// window.location and scope data supplies `transaction` during prepareEvent),
// so an event captured right before a redirect would otherwise be tagged with
// the destination page. The location is snapshotted now, at call time, and
// re-applied via a scope event processor.
//
// This override is deterministic, not a race with httpContext: httpContext sets
// request.url in the SDK's `preprocessEvent` phase, which runs before ANY event
// processor, and scope event processors run last of all processors (see
// @sentry/core `prepareEvent`). So this processor reliably wins.
function withCurrentLocation() {
    const url = window.location.href;
    const transaction = window.location.pathname;
    return (scope) => {
        scope.addEventProcessor((event) => {
            event.request = { ...event.request, url };
            event.transaction = transaction;
            return event;
        });
        return scope;
    };
}

export { getTag, itemsInCart, withCurrentLocation };