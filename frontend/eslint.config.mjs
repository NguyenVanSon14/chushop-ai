import nextVitals from "eslint-config-next/core-web-vitals";
import nextTypeScript from "eslint-config-next/typescript";

const eslintConfig = [
  ...nextVitals,
  ...nextTypeScript,
  { ignores: ["next-env.d.ts", ".next/**"] },
];

export default eslintConfig;
