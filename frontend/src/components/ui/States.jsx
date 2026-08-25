import { AlertTriangle, Inbox, Loader2 } from "lucide-react";

export function Spinner({ label = "Loading…" }) {
  return (
    <div className="card flex flex-col items-center justify-center gap-3 py-16 text-slate-500">
      <Loader2 className="animate-spin text-accent-500" size={26} />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function ErrorState({ message = "Something went wrong." }) {
  return (
    <div className="card flex flex-col items-center justify-center gap-3 border-red-500/20 bg-red-500/5 py-14 text-center">
      <AlertTriangle className="text-red-400" size={24} />
      <p className="max-w-sm text-sm text-red-300">{message}</p>
    </div>
  );
}

export function EmptyState({ message = "Nothing to show yet." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-14 text-center text-slate-600">
      <Inbox size={24} />
      <p className="text-sm">{message}</p>
    </div>
  );
}
