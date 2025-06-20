import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

// Disable ESLint completely during builds
const eslintConfig = process.env.NODE_ENV === 'production' ? [] : [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
];

export default eslintConfig;
