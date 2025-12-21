import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getUserData } from '@/utils/authUtils';

interface Notification {
    id: number;
    title: string;
    message: string;
    type: string;
    read: boolean;
    created_at: string;
    post_id?: number;
}

const API_BASE_URL = 'http://localhost:5000/api';

export const NotificationBell = () => {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);

    useEffect(() => {
        fetchNotifications();
        // Poll for new notifications every 15 seconds
        const interval = setInterval(fetchNotifications, 15000);
        return () => clearInterval(interval);
    }, []);

    const fetchNotifications = async () => {
        try {
            const user = getUserData();
            const userId = user?.id;

            if (!userId) return;

            // Use full API URL instead of relative URL
            const response = await fetch(`${API_BASE_URL}/notifications/${userId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                const notifs = data.data.notifications || [];
                setNotifications(notifs.slice(0, 5)); // Show only latest 5
                setUnreadCount(notifs.filter((n: Notification) => !n.read).length);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
            // Don't show error to user, just log it
        }
    };

    const markAsRead = async (notificationId: number) => {
        try {
            // Use full API URL
            const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
                method: 'PUT',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            fetchNotifications();
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    };

    const handleNotificationClick = (notification: Notification) => {
        markAsRead(notification.id);
        setShowDropdown(false);

        // Navigate to issue if post_id exists
        if (notification.post_id) {
            window.location.href = `/issue/${notification.post_id}`;
        }
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'completion_verification':
                return '🔔';
            case 'user_verified':
                return '✅';
            case 'user_rejected':
                return '❌';
            case 'status_update':
                return '📝';
            default:
                return '📢';
        }
    };

    const formatTime = (timestamp: string) => {
        try {
            // Parse the UTC timestamp from backend
            const date = new Date(timestamp);
            // Get current time in UTC
            const now = new Date();

            // Calculate difference in milliseconds
            const diff = now.getTime() - date.getTime();
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(minutes / 60);
            const days = Math.floor(hours / 24);

            if (minutes < 1) return 'now';
            if (minutes < 60) return `${minutes}m ago`;
            if (hours < 24) return `${hours}h ago`;
            return `${days}d ago`;
        } catch {
            return '';
        }
    };

    return (
        <div className="relative">
            <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
            >
                <Bell className="h-6 w-6" />
                {/* Red dot badge for unread notifications */}
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {showDropdown && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-10"
                        onClick={() => setShowDropdown(false)}
                    />

                    {/* Dropdown */}
                    <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-20 max-h-96 overflow-y-auto">
                        <div className="p-4 border-b border-gray-200">
                            <h3 className="font-semibold text-gray-800">Notifications</h3>
                        </div>

                        {notifications.length === 0 ? (
                            <div className="p-8 text-center text-gray-500">
                                <Bell className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                                <p>No notifications yet</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-100">
                                {notifications.map((notification) => (
                                    <div
                                        key={notification.id}
                                        onClick={() => handleNotificationClick(notification)}
                                        className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${!notification.read ? 'bg-blue-50' : ''
                                            }`}
                                    >
                                        <div className="flex items-start gap-3">
                                            <span className="text-2xl">
                                                {getNotificationIcon(notification.type)}
                                            </span>
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium text-sm text-gray-900 mb-1">
                                                    {notification.title}
                                                </p>
                                                <p className="text-sm text-gray-600 line-clamp-2">
                                                    {notification.message}
                                                </p>
                                                <p className="text-xs text-gray-400 mt-1">
                                                    {formatTime(notification.created_at)}
                                                </p>
                                            </div>
                                            {!notification.read && (
                                                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {notifications.length > 0 && (
                            <div className="p-3 border-t border-gray-200 text-center">
                                <button
                                    onClick={() => {
                                        setShowDropdown(false);
                                        // Could navigate to a full notifications page
                                    }}
                                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                                >
                                    View all notifications
                                </button>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};