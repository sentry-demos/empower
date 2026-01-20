/**
 * Tests for Real-time Collection Manager
 * Verifies the fix for TypeError: Object has no method 'updateFrom'
 */

import { Model, Collection, RealtimeManager } from '../utils/realtimeCollection';

describe('Model', () => {
    test('should create a model with attributes', () => {
        const model = new Model({ id: 1, name: 'Test', version: 1 });
        expect(model.get('id')).toBe(1);
        expect(model.get('name')).toBe('Test');
        expect(model.get('version')).toBe(1);
    });

    test('should update from another model instance', () => {
        const model1 = new Model({ id: 1, name: 'Original', version: 1 });
        const model2 = new Model({ id: 1, name: 'Updated', version: 2 });
        
        model1.updateFrom(model2);
        
        expect(model1.get('name')).toBe('Updated');
        expect(model1.version).toBe(2);
    });

    test('should update from plain JSON object (FIX)', () => {
        const model = new Model({ id: 1, name: 'Original', version: 1 });
        const plainObject = { id: 1, name: 'Updated', version: 2 };
        
        // This should not throw TypeError
        expect(() => {
            model.updateFrom(plainObject);
        }).not.toThrow();
        
        expect(model.get('name')).toBe('Updated');
        expect(model.version).toBe(2);
    });

    test('should set and get attributes', () => {
        const model = new Model({ id: 1 });
        model.set('name', 'Test');
        expect(model.get('name')).toBe('Test');
    });

    test('should convert to JSON', () => {
        const model = new Model({ id: 1, name: 'Test', version: 1 });
        const json = model.toJSON();
        expect(json).toEqual({ id: 1, name: 'Test', version: 1 });
    });
});

describe('Collection', () => {
    test('should add a model instance', () => {
        const collection = new Collection();
        const model = new Model({ id: 1, name: 'Test' });
        
        collection.add(model);
        
        expect(collection.get(1)).toBe(model);
        expect(collection.toArray()).toHaveLength(1);
    });

    test('should add a plain JSON object and convert to model (FIX)', () => {
        const collection = new Collection();
        const plainObject = { id: 1, name: 'Test', version: 1 };
        
        // This should not throw TypeError - the fix converts JSON to model
        expect(() => {
            collection.add(plainObject);
        }).not.toThrow();
        
        const model = collection.get(1);
        expect(model).toBeInstanceOf(Model);
        expect(model.get('name')).toBe('Test');
    });

    test('should merge existing model with plain JSON object (FIX)', () => {
        const collection = new Collection();
        
        // Add initial model
        collection.add({ id: 1, name: 'Original', version: 1 });
        
        // Merge with plain JSON object (simulating AJAX response)
        const plainObject = { id: 1, name: 'Updated', version: 2 };
        
        // This was causing the TypeError before the fix
        expect(() => {
            collection.add(plainObject, { merge: true });
        }).not.toThrow();
        
        const model = collection.get(1);
        expect(model.get('name')).toBe('Updated');
        expect(model.get('version')).toBe(2);
    });

    test('should not merge when version is older', () => {
        const collection = new Collection();
        
        // Add initial model with version 2
        collection.add({ id: 1, name: 'Current', version: 2 });
        
        // Try to merge with older version
        collection.add({ id: 1, name: 'Old', version: 1 }, { merge: true });
        
        const model = collection.get(1);
        expect(model.get('name')).toBe('Current');
        expect(model.get('version')).toBe(2);
    });

    test('should remove a model', () => {
        const collection = new Collection();
        const model = new Model({ id: 1, name: 'Test' });
        
        collection.add(model);
        expect(collection.toArray()).toHaveLength(1);
        
        collection.remove(model);
        expect(collection.toArray()).toHaveLength(0);
        expect(collection.get(1)).toBeUndefined();
    });

    test('should get model index', () => {
        const collection = new Collection();
        const model1 = new Model({ id: 1 });
        const model2 = new Model({ id: 2 });
        
        collection.add(model1);
        collection.add(model2);
        
        expect(collection.indexOf(model1)).toBe(0);
        expect(collection.indexOf(model2)).toBe(1);
    });

    test('should handle multiple additions without errors', () => {
        const collection = new Collection();
        
        // Simulate real-time updates with plain JSON objects
        const updates = [
            { id: 1, name: 'User 1', version: 1 },
            { id: 2, name: 'User 2', version: 1 },
            { id: 1, name: 'User 1 Updated', version: 2 },
            { id: 3, name: 'User 3', version: 1 }
        ];
        
        expect(() => {
            updates.forEach(update => {
                collection.add(update, { merge: true });
            });
        }).not.toThrow();
        
        expect(collection.toArray()).toHaveLength(3);
        expect(collection.get(1).get('name')).toBe('User 1 Updated');
    });
});

describe('RealtimeManager', () => {
    test('should create a realtime manager', () => {
        const manager = new RealtimeManager({
            pollUrl: '/api/test',
            pollTime: 1000
        });
        
        expect(manager.collection).toBeInstanceOf(Collection);
        expect(manager.options.pollUrl).toBe('/api/test');
        expect(manager.options.pollTime).toBe(1000);
    });

    test('should merge plain JSON data without errors (FIX)', () => {
        const manager = new RealtimeManager();
        
        // Simulate server response with plain JSON
        const jsonData = { id: 1, name: 'Test User', version: 1 };
        
        // This was causing the TypeError before the fix
        expect(() => {
            manager.merge(jsonData);
        }).not.toThrow();
        
        const model = manager.collection.get(1);
        expect(model).toBeInstanceOf(Model);
        expect(model.get('name')).toBe('Test User');
    });

    test('should handle multiple merges correctly', () => {
        const manager = new RealtimeManager();
        
        // Simulate multiple updates
        manager.merge({ id: 1, name: 'User 1', version: 1 });
        manager.merge({ id: 2, name: 'User 2', version: 1 });
        manager.merge({ id: 1, name: 'User 1 Updated', version: 2 });
        
        expect(manager.collection.toArray()).toHaveLength(2);
        expect(manager.collection.get(1).get('name')).toBe('User 1 Updated');
        expect(manager.collection.get(2).get('name')).toBe('User 2');
    });

    test('should start and stop polling', () => {
        jest.useFakeTimers();
        const manager = new RealtimeManager({
            pollUrl: '/api/test',
            pollTime: 1000
        });
        
        manager.startPolling();
        expect(manager.isPolling).toBe(true);
        
        manager.stopPolling();
        expect(manager.isPolling).toBe(false);
        
        jest.useRealTimers();
    });

    test('should handle poll with mocked fetch (FIX)', async () => {
        // Mock fetch
        global.fetch = jest.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve({
                    cursor: 'abc123',
                    members: [
                        { id: 1, name: 'User 1', version: 1 },
                        { id: 2, name: 'User 2', version: 1 }
                    ]
                })
            })
        );
        
        const updateCallback = jest.fn();
        const manager = new RealtimeManager({
            pollUrl: '/api/updates',
            realtime: true,
            onUpdate: updateCallback
        });
        
        await manager.poll();
        
        // Verify the plain JSON objects were processed without errors
        expect(manager.collection.toArray()).toHaveLength(2);
        expect(manager.collection.get(1).get('name')).toBe('User 1');
        expect(manager.collection.get(2).get('name')).toBe('User 2');
        expect(manager.cursor).toBe('abc123');
        expect(updateCallback).toHaveBeenCalledWith(manager.collection);
        
        // Cleanup
        global.fetch.mockClear();
        delete global.fetch;
    });

    test('should handle poll errors gracefully', async () => {
        // Mock fetch to throw error
        global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));
        
        const errorCallback = jest.fn();
        const manager = new RealtimeManager({
            pollUrl: '/api/updates',
            realtime: true,
            onError: errorCallback
        });
        
        await manager.poll();
        
        expect(errorCallback).toHaveBeenCalledWith(expect.any(Error));
        
        // Cleanup
        global.fetch.mockClear();
        delete global.fetch;
    });

    test('should remove member', () => {
        const manager = new RealtimeManager();
        
        manager.merge({ id: 1, name: 'User 1', version: 1 });
        const model = manager.collection.get(1);
        
        manager.removeMember(model);
        
        expect(manager.collection.toArray()).toHaveLength(0);
        expect(manager.collection.get(1)).toBeUndefined();
    });
});

describe('Integration: Real-time Update Scenario (Bug Reproduction & Fix)', () => {
    test('should handle complete real-time update flow without TypeError', async () => {
        // This test reproduces the exact scenario from the bug report
        
        // 1. User navigates to dashboard, triggering real-time updates
        const manager = new RealtimeManager({
            pollUrl: '/api/dashboard/updates',
            realtime: true,
            pollTime: 3000
        });
        
        // 2. Initial data loaded
        manager.merge({ id: 1, name: 'Item 1', version: 1 });
        manager.merge({ id: 2, name: 'Item 2', version: 1 });
        
        expect(manager.collection.toArray()).toHaveLength(2);
        
        // 3. Real-time poll returns plain JSON objects (simulating AJAX response)
        global.fetch = jest.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve({
                    members: [
                        { id: 1, name: 'Item 1 Updated', version: 2 }, // Update existing
                        { id: 3, name: 'Item 3', version: 1 }           // New item
                    ]
                })
            })
        );
        
        // 4. Poll processes the response
        // BEFORE FIX: This would throw TypeError: Object has no method 'updateFrom'
        // AFTER FIX: Plain JSON objects are converted to model instances
        await expect(manager.poll()).resolves.not.toThrow();
        
        // 5. Verify the collection was updated correctly
        expect(manager.collection.toArray()).toHaveLength(3);
        expect(manager.collection.get(1).get('name')).toBe('Item 1 Updated');
        expect(manager.collection.get(1).get('version')).toBe(2);
        expect(manager.collection.get(3).get('name')).toBe('Item 3');
        
        // 6. Verify all items are proper model instances with updateFrom method
        manager.collection.toArray().forEach(model => {
            expect(model).toBeInstanceOf(Model);
            expect(typeof model.updateFrom).toBe('function');
        });
        
        // Cleanup
        global.fetch.mockClear();
        delete global.fetch;
    });
});
