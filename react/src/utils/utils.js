import * as Sentry from '@sentry/react';

function getTag(tag) {
    return Sentry.getCurrentScope()._tags[tag]
}

function itemsInCart(cart) {
    return Object.values(cart).reduce((a, b) => a + b, 0)
}

export { getTag, itemsInCart };