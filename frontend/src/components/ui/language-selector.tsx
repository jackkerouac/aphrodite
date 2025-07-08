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
  { code: "ar", name: "Arabic", native_name: "العربية" },
  { code: "zh", name: "Chinese", native_name: "中文" },
  { code: "cs", name: "Czech", native_name: "Čeština" },
  { code: "da", name: "Danish", native_name: "Dansk" },
  { code: "nl", name: "Dutch", native_name: "Nederlands" },
  { code: "fi", name: "Finnish", native_name: "Suomi" },
  { code: "fr", name: "French", native_name: "Français" },
  { code: "de", name: "German", native_name: "Deutsch" },
  { code: "he", name: "Hebrew", native_name: "עברית" },
  { code: "hi", name: "Hindi", native_name: "हिन्दी" },
  { code: "hu", name: "Hungarian", native_name: "Magyar" },
  { code: "it", name: "Italian", native_name: "Italiano" },
  { code: "ja", name: "Japanese", native_name: "日本語" },
  { code: "ko", name: "Korean", native_name: "한국어" },
  { code: "no", name: "Norwegian", native_name: "Norsk" },
  { code: "pl", name: "Polish", native_name: "Polski" },
  { code: "pt", name: "Portuguese", native_name: "Português" },
  { code: "ru", name: "Russian", native_name: "Русский" },
  { code: "es", name: "Spanish", native_name: "Español" },
  { code: "sv", name: "Swedish", native_name: "Svenska" },
  { code: "ta", name: "Tamil", native_name: "தமிழ்" },
  { code: "th", name: "Thai", native_name: "ไทย" },
  { code: "tr", name: "Turkish", native_name: "Türkçe" },
  { code: "null", name: "No Language (Textless)", native_name: "Textless" },
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
