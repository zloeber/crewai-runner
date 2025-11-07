/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CREWAI_RUNNER_API_HOST: string
  readonly VITE_CREWAI_API_TOKEN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
