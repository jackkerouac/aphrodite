import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { getCombinedFontList, FontSelectProps } from '@/lib/font-utils';

export function FontSelect({ value, onValueChange, availableFonts = [], placeholder = 'Select a font...', disabled = false }: FontSelectProps) {
  const fontOptions = getCombinedFontList(availableFonts);

  return (
    <Select
      value={value}
      onValueChange={onValueChange}
      disabled={disabled}
    >
      <SelectTrigger>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {fontOptions.map((font) => (
          <SelectItem key={font} value={font}>
            {font}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
