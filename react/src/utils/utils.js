import configureScope from '@sentry/react';

function getTag(tag) {
    configureScope((scope) => {
        const tags = scope._tags; // _tags contains the current tags set
        return tags[tag]
    });
}

function itemsInCart(cart) {
    return Object.values(cart).reduce((a, b) => a + b, 0)
}

export { getTag, itemsInCart };