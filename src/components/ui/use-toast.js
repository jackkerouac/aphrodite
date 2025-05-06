import { useEffect, useState } from "react"

const TOAST_REMOVE_DELAY = 1000000
const TOAST_DURATION = 5000

const actionTypes = {
  ADD_TOAST: "ADD_TOAST",
  UPDATE_TOAST: "UPDATE_TOAST",
  DISMISS_TOAST: "DISMISS_TOAST",
  REMOVE_TOAST: "REMOVE_TOAST",
}

let count = 0

function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER
  return count.toString()
}

const toastTimeouts = new Map()

function createToast(props) {
  const id = genId()
  const toast = {
    id,
    ...props,
    open: true,
    onOpenChange: (open) => {
      if (!open) {
        dismissToast(id)
      }
    },
  }

  return toast
}

function dismissToast(id) {
  if (toastTimeouts.has(id)) {
    clearTimeout(toastTimeouts.get(id))
    toastTimeouts.delete(id)
  }

  // Simulate dismissal action
  const toast = toasts.find((t) => t.id === id)
  if (toast) {
    toast.open = false
    updateToasts([...toasts])

    setTimeout(() => {
      removeToast(id)
    }, TOAST_REMOVE_DELAY)
  }
}

function removeToast(id) {
  const newToasts = toasts.filter((t) => t.id !== id)
  updateToasts(newToasts)
}

// Global state for toasts
let toasts = []
let updateToasts = (newToasts) => {
  toasts = newToasts
  listeners.forEach((listener) => listener(toasts))
}

const listeners = new Set()

export function useToast() {
  const [state, setState] = useState(toasts)

  useEffect(() => {
    listeners.add(setState)
    return () => listeners.delete(setState)
  }, [])

  return {
    toasts: state,
    toast: (props) => {
      const toast = createToast(props)
      updateToasts([...toasts, toast])

      // Auto-dismiss
      const timeoutId = setTimeout(() => {
        dismissToast(toast.id)
      }, props.duration || TOAST_DURATION)

      toastTimeouts.set(toast.id, timeoutId)
      return toast.id
    },
    dismiss: (id) => {
      if (id) {
        dismissToast(id)
      } else {
        toasts.forEach((toast) => dismissToast(toast.id))
      }
    },
  }
}

export const toast = {
  dismiss: (id) => {
    if (id) {
      dismissToast(id)
    } else {
      toasts.forEach((toast) => dismissToast(toast.id))
    }
  },
  custom: (props) => {
    const toast = createToast(props)
    updateToasts([...toasts, toast])

    // Auto-dismiss
    const timeoutId = setTimeout(() => {
      dismissToast(toast.id)
    }, props.duration || TOAST_DURATION)

    toastTimeouts.set(toast.id, timeoutId)
    return toast.id
  },
}
