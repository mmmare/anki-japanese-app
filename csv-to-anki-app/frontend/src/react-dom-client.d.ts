declare module 'react-dom/client' {
  import { Root } from 'react-dom';
  
  export function createRoot(
    container: Element | DocumentFragment | null,
    options?: { hydrate?: boolean }
  ): Root;
  
  export interface Root {
    render(children: React.ReactNode): void;
    unmount(): void;
  }
}