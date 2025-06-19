/**
 * NotificationToast Component
 * 
 * Progress and completion notifications
 */

import React, { useEffect } from 'react'
import { toast } from 'sonner'
import { CheckCircle, AlertCircle, Clock } from 'lucide-react'

interface NotificationData {
  type: 'success' | 'error' | 'progress' | 'info'
  title: string
  message?: string
  duration?: number
}

interface NotificationToastProps {
  notification: NotificationData | null
  onDismiss?: () => void
}

export const NotificationToast: React.FC<NotificationToastProps> = ({
  notification,
  onDismiss
}) => {
  useEffect(() => {
    if (!notification) return

    const { type, title, message, duration = 4000 } = notification

    const getIcon = () => {
      switch (type) {
        case 'success': return <CheckCircle className="w-4 h-4" />
        case 'error': return <AlertCircle className="w-4 h-4" />
        case 'progress': return <Clock className="w-4 h-4" />
        case 'info': return <Clock className="w-4 h-4" />
        default: return null
      }
    }

    const toastContent = (
      <div className="flex items-center space-x-3">
        {getIcon()}
        <div className="flex-1">
          <div className="font-medium">{title}</div>
          {message && (
            <div className="text-sm text-muted-foreground mt-1">
              {message}
            </div>
          )}
        </div>
      </div>
    )

    switch (type) {
      case 'success':
        toast.success(toastContent, { duration })
        break
      case 'error':
        toast.error(toastContent, { duration: duration * 2 }) // Errors stay longer
        break
      case 'progress':
      case 'info':
        toast.info(toastContent, { duration })
        break
    }

    // Call dismiss callback if provided
    const timer = setTimeout(() => {
      onDismiss?.()
    }, duration)

    return () => clearTimeout(timer)
  }, [notification, onDismiss])

  return null // This component doesn't render anything directly
}
