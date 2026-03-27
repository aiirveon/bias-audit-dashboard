"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { key: "analyser",  label: "ANALYSER",         href: "/" },
  { key: "simulator", label: "SIMULATOR",         href: "/simulator" },
  { key: "dashboard", label: "AUDIT DASHBOARD",   href: "/dashboard" },
];

export function TopNav() {
  const pathname = usePathname();
  return (
    <nav className="border-b border-border bg-panel-dark shrink-0">
      <div className="flex items-center justify-between px-5 h-14 relative">
        <div className="flex flex-col leading-none">
          <span className="text-base font-black tracking-tight text-foreground">BIAS AUDIT</span>
          <span className="text-[10px] font-light tracking-wide text-muted-foreground">dashboard</span>
        </div>
        <div className="absolute left-1/2 -translate-x-1/2 flex items-center gap-8">
          {NAV_ITEMS.map(item => {
            const active = pathname === item.href;
            return (
              <Link key={item.key} href={item.href}
                className={`relative py-4 text-[11px] tracking-widest transition-colors ${
                  active ? "text-foreground" : "text-muted-foreground hover:text-foreground/70"
                }`}>
                {item.label}
                {active && <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-primary" />}
              </Link>
            );
          })}
        </div>
        <div className="w-[80px]" />
      </div>
    </nav>
  );
}
