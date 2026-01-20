/**
 * Real-time Dashboard Component
 * Demonstrates the fix for TypeError: Object has no method 'updateFrom'
 * 
 * This component uses the RealtimeManager to safely handle real-time updates
 * from server responses containing plain JSON objects.
 */

import React, { useEffect, useState, useCallback } from 'react';
import RealtimeManager, { Model } from '../utils/realtimeCollection';

/**
 * Custom model for dashboard items
 */
class DashboardItemModel extends Model {
    constructor(attributes) {
        super(attributes);
    }

    // Add custom methods specific to dashboard items
    isNew() {
        return this.get('createdAt') > Date.now() - 5000; // New if created in last 5 seconds
    }

    getDisplayName() {
        return this.get('name') || 'Untitled Item';
    }
}

/**
 * Real-time Dashboard Component
 * 
 * Features:
 * - Polls server for updates every 3 seconds
 * - Displays items in real-time without page refresh
 * - Handles version conflicts (newer data takes precedence)
 * - Shows connection status and error messages
 * - Prevents TypeError by using the RealtimeManager
 */
function RealtimeDashboard({ pollUrl = '/api/dashboard/items' }) {
    const [items, setItems] = useState([]);
    const [status, setStatus] = useState('connecting');
    const [error, setError] = useState(null);
    const [manager, setManager] = useState(null);

    // Handle collection updates
    const handleUpdate = useCallback((collection) => {
        // Convert models to plain objects for React state
        const itemsArray = collection.toArray().map(model => ({
            ...model.toJSON(),
            isNew: model.isNew(),
            displayName: model.getDisplayName()
        }));
        
        setItems(itemsArray);
        setStatus('connected');
        setError(null);
    }, []);

    // Handle errors
    const handleError = useCallback((err) => {
        console.error('Real-time update error:', err);
        setError(err.message);
        setStatus('error');
    }, []);

    // Initialize real-time manager
    useEffect(() => {
        const realtimeManager = new RealtimeManager({
            ModelClass: DashboardItemModel,
            pollUrl: pollUrl,
            pollTime: 3000, // Poll every 3 seconds
            realtime: true,
            onUpdate: handleUpdate,
            onError: handleError
        });

        setManager(realtimeManager);
        realtimeManager.startPolling();

        // Cleanup on unmount
        return () => {
            realtimeManager.stopPolling();
        };
    }, [pollUrl, handleUpdate, handleError]);

    // Manual refresh
    const handleRefresh = () => {
        if (manager) {
            setStatus('refreshing');
            manager.poll();
        }
    };

    return (
        <div className="realtime-dashboard">
            <div className="dashboard-header">
                <h1>Real-time Dashboard</h1>
                <div className="dashboard-controls">
                    <span className={`status-indicator status-${status}`}>
                        {status === 'connected' && '🟢 Connected'}
                        {status === 'connecting' && '🟡 Connecting...'}
                        {status === 'error' && '🔴 Error'}
                        {status === 'refreshing' && '🔄 Refreshing...'}
                    </span>
                    <button onClick={handleRefresh} disabled={!manager}>
                        Refresh
                    </button>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    ⚠️ Error: {error}
                </div>
            )}

            <div className="dashboard-content">
                {items.length === 0 ? (
                    <div className="empty-state">
                        <p>No items yet. Waiting for updates...</p>
                    </div>
                ) : (
                    <div className="items-grid">
                        {items.map(item => (
                            <DashboardItem 
                                key={item.id} 
                                item={item}
                            />
                        ))}
                    </div>
                )}
            </div>

            <div className="dashboard-footer">
                <p>
                    {items.length} {items.length === 1 ? 'item' : 'items'} • 
                    Last updated: {new Date().toLocaleTimeString()}
                </p>
                <p className="fix-notice">
                    ✅ Using fixed RealtimeManager (no updateFrom TypeError)
                </p>
            </div>
        </div>
    );
}

/**
 * Individual dashboard item component
 */
function DashboardItem({ item }) {
    return (
        <div className={`dashboard-item ${item.isNew ? 'new-item' : ''}`}>
            <div className="item-header">
                <h3>{item.displayName}</h3>
                {item.isNew && <span className="badge">NEW</span>}
            </div>
            <div className="item-details">
                <p><strong>ID:</strong> {item.id}</p>
                <p><strong>Version:</strong> {item.version}</p>
                {item.description && (
                    <p className="item-description">{item.description}</p>
                )}
            </div>
            {item.updatedAt && (
                <div className="item-footer">
                    Updated: {new Date(item.updatedAt).toLocaleString()}
                </div>
            )}
        </div>
    );
}

/**
 * Example usage in a parent component:
 * 
 * import RealtimeDashboard from './components/RealtimeDashboard';
 * 
 * function App() {
 *     return (
 *         <div>
 *             <RealtimeDashboard pollUrl="/api/dashboard/items" />
 *         </div>
 *     );
 * }
 */

export default RealtimeDashboard;

/**
 * Example server endpoint response format:
 * 
 * GET /api/dashboard/items?cursor=abc123
 * 
 * Response:
 * {
 *     "cursor": "def456",
 *     "members": [
 *         {
 *             "id": 1,
 *             "name": "Dashboard Item 1",
 *             "description": "This is an example item",
 *             "version": 2,
 *             "createdAt": 1642713600000,
 *             "updatedAt": 1642713660000
 *         },
 *         {
 *             "id": 2,
 *             "name": "Dashboard Item 2",
 *             "version": 1,
 *             "createdAt": 1642713700000
 *         }
 *     ]
 * }
 * 
 * The RealtimeManager will:
 * 1. Receive these plain JSON objects
 * 2. Convert them to DashboardItemModel instances
 * 3. Merge them into the collection safely (no TypeError!)
 * 4. Respect version numbers to prevent data corruption
 * 5. Trigger the onUpdate callback with the updated collection
 */
