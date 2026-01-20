/**
 * Real-time Collection Manager
 * 
 * This module provides utilities for managing real-time data updates
 * and fixes the TypeError: Object has no method 'updateFrom' issue
 * that occurs when plain JSON objects are passed to collection merge operations.
 */

/**
 * Base Model class that provides updateFrom functionality
 */
export class Model {
    constructor(attributes = {}) {
        this.attributes = { ...attributes };
        this.id = attributes.id;
        this.version = attributes.version || 0;
    }

    get(key) {
        return this.attributes[key];
    }

    set(key, value) {
        this.attributes[key] = value;
        return this;
    }

    /**
     * Updates this model from another model or plain object
     * This is the method that was missing and causing the TypeError
     */
    updateFrom(source) {
        if (source instanceof Model) {
            this.attributes = { ...this.attributes, ...source.attributes };
        } else if (typeof source === 'object') {
            this.attributes = { ...this.attributes, ...source };
        }
        if (source.version !== undefined) {
            this.version = source.version;
        }
        return this;
    }

    toJSON() {
        return { ...this.attributes };
    }
}

/**
 * Collection class for managing groups of models
 */
export class Collection {
    constructor(ModelClass = Model) {
        this.models = [];
        this.ModelClass = ModelClass;
        this._byId = {};
    }

    /**
     * Get a model by ID
     */
    get(id) {
        return this._byId[id];
    }

    /**
     * Get the index of a model in the collection
     */
    indexOf(model) {
        return this.models.indexOf(model);
    }

    /**
     * Add or merge a model into the collection
     * FIX: Ensures plain JSON objects are converted to model instances
     * before attempting to merge
     */
    add(data, options = {}) {
        const { merge = false, sort = false } = options;

        // FIX: Convert plain JSON object to model instance if needed
        let model;
        if (data instanceof Model) {
            model = data;
        } else {
            // Create a new model instance from plain JSON data
            model = new this.ModelClass(data);
        }

        const existing = this.get(model.id);

        if (existing) {
            if (merge) {
                // Version check to prevent overwriting newer data with older data
                if (existing.get('version') > model.get('version')) {
                    return existing;
                }
                // FIX: Now updateFrom is available because both are model instances
                existing.updateFrom(model);
                return existing;
            } else {
                // Replace the existing model
                const index = this.indexOf(existing);
                this.models[index] = model;
                this._byId[model.id] = model;
            }
        } else {
            // Add new model
            this.models.push(model);
            this._byId[model.id] = model;
        }

        if (sort && this.comparator) {
            this.sort();
        }

        return model;
    }

    /**
     * Remove a model from the collection
     */
    remove(model) {
        const index = this.indexOf(model);
        if (index !== -1) {
            this.models.splice(index, 1);
            delete this._byId[model.id];
        }
        return this;
    }

    /**
     * Sort the collection
     */
    sort() {
        if (this.comparator) {
            this.models.sort(this.comparator);
        }
        return this;
    }

    /**
     * Get all models
     */
    toArray() {
        return [...this.models];
    }
}

/**
 * Real-time polling manager
 * Demonstrates the corrected pattern for handling real-time updates
 */
export class RealtimeManager {
    constructor(options = {}) {
        this.options = {
            realtime: true,
            pollTime: 3000,
            pollUrl: null,
            ...options
        };
        this.collection = new Collection(options.ModelClass);
        this.cursor = null;
        this.isPolling = false;
    }

    /**
     * Start real-time polling
     */
    startPolling() {
        if (!this.isPolling) {
            this.isPolling = true;
            this.poll();
        }
    }

    /**
     * Stop real-time polling
     */
    stopPolling() {
        this.isPolling = false;
        if (this.pollTimeout) {
            clearTimeout(this.pollTimeout);
        }
    }

    /**
     * Poll for new data
     * FIX: Properly handles JSON responses by converting to model instances
     */
    async poll() {
        if (!this.options.realtime || !this.options.pollUrl) {
            this.pollTimeout = setTimeout(() => this.poll(), this.options.pollTime);
            return;
        }

        try {
            const params = new URLSearchParams();
            if (this.cursor) {
                params.append('cursor', this.cursor);
            }

            const url = `${this.options.pollUrl}?${params.toString()}`;
            const response = await fetch(url);
            const data = await response.json();

            // Update cursor for next poll
            if (data.cursor) {
                this.cursor = data.cursor;
            }

            // FIX: Process each item from the response
            if (data.members && Array.isArray(data.members)) {
                data.members.forEach(memberData => {
                    // The collection.add method will now properly handle
                    // plain JSON objects by converting them to model instances
                    this.merge(memberData, { sort: true });
                });
            }

            // Trigger callback if provided
            if (this.options.onUpdate) {
                this.options.onUpdate(this.collection);
            }
        } catch (error) {
            console.error('Polling error:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
        }

        // Schedule next poll
        if (this.isPolling) {
            this.pollTimeout = setTimeout(() => this.poll(), this.options.pollTime);
        }
    }

    /**
     * Merge a member into the collection
     * FIX: Ensures plain JSON objects are converted before merging
     */
    merge(memberData, options = {}) {
        // The collection.add method handles the conversion from plain JSON
        // to model instance, preventing the "updateFrom" TypeError
        this.collection.add(memberData, {
            merge: true,
            sort: options.sort !== false
        });
    }

    /**
     * Remove a member from the collection
     */
    removeMember(member) {
        this.collection.remove(member);
    }

    /**
     * Get the collection
     */
    getCollection() {
        return this.collection;
    }
}

/**
 * Example usage demonstrating the fix:
 * 
 * // Create a custom model class
 * class UserModel extends Model {
 *     constructor(attributes) {
 *         super(attributes);
 *     }
 * }
 * 
 * // Create a realtime manager
 * const manager = new RealtimeManager({
 *     ModelClass: UserModel,
 *     pollUrl: '/api/users/updates',
 *     pollTime: 3000,
 *     realtime: true,
 *     onUpdate: (collection) => {
 *         console.log('Collection updated:', collection.toArray());
 *     }
 * });
 * 
 * // Start polling
 * manager.startPolling();
 * 
 * // When JSON data comes from the server:
 * // { id: 1, name: 'John', version: 2 }
 * // It will be automatically converted to a UserModel instance
 * // before being merged, preventing the TypeError
 */

export default RealtimeManager;
