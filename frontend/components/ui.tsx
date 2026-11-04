import {clsx} from "clsx";
import type {ButtonHTMLAttributes, HTMLAttributes} from "react";

export function Card({className, ...props}: HTMLAttributes<HTMLDivElement>) {
  return <div className={clsx("min-w-0 rounded-md border border-white/10 bg-panel p-5 shadow-glow", className)} {...props} />;
}

export function Button({className, ...props}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={clsx("focus-ring rounded-md bg-trust px-4 py-2 text-sm font-semibold text-[#09231d] hover:bg-[#55d6ba]", className)}
      {...props}
    />
  );
}

export function SectionTitle({title, subtitle}: {title: string; subtitle?: string}) {
  return (
    <div className="mb-5">
      <h1 className="text-2xl font-semibold tracking-normal">{title}</h1>
      {subtitle ? <p className="mt-1 max-w-3xl break-words text-sm text-muted">{subtitle}</p> : null}
    </div>
  );
}
