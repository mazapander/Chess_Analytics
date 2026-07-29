import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">CA</div>
        <nav aria-label="Navegación principal">
          <a className="nav-item active" href="#overview">Resumen</a>
          <a className="nav-item" href="#games">Partidas</a>
          <a className="nav-item" href="#patterns">Patrones</a>
          <a className="nav-item disabled" href="#training" aria-disabled="true">Entrenamiento</a>
        </nav>
        <div className="sidebar-user">
          <span className="status-dot" />
          <div><strong>mazapander0</strong><small>Chess.com</small></div>
        </div>
      </aside>
      <main className="page-content">{children}</main>
    </div>
  );
}
