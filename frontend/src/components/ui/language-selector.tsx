/**
 * Language Selector Component
 * 
 * Reusable component for selecting poster languages in bulk operations
 */

import React from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"

export interface LanguageOption {
  code: string
  name: string
  native_name: string
}

const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: "en", name: "English", native_name: "English" },
  { code: "de", name: "German", native_name: "Deutsch" },
  { code: "fr", name: "French", native_name: "Français" },
  { code: "es", name: "Spanish", native_name: "Español" },
  { code: "it", name: "Italian", native_name: "Italiano" },
  { code: "ja", name: "Japanese", native_name: "日本語" },
  { code: "ko", name: "Korean", native_name: "한국어" },
  { code: "zh", name: "Chinese", native_name: "中文" },
]

interface LanguageSelectorProps {
  value: string
  onValueChange: (value: string) => void
  disabled?: boolean
  label?: string
  placeholder?: string
  className?: string
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  value,
  onValueChange,
  disabled = false,
  label = "Language Preference",
  placeholder = "Select language...",
  className = ""
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <Label htmlFor="language-selector">
          {label}
        </Label>
      )}
      <Select 
        value={value} 
        onValueChange={onValueChange}
        disabled={disabled}
      >
        <SelectTrigger id="language-selector">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {SUPPORTED_LANGUAGES.map((lang) => (
            <SelectItem key={lang.code} value={lang.code}>
              <div className="flex items-center space-x-2">
                <span>{lang.name}</span>
                <span className="text-muted-foreground">({lang.native_name})</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

export { SUPPORTED_LANGUAGES }
export type { LanguageOption }
