const ICON_TONES = {
  neutral: "bg-slate-500/10 text-slate-300",
  danger: "bg-red-500/10 text-red-400",
  success: "bg-emerald-500/10 text-emerald-400",
  warning: "bg-amber-500/10 text-amber-400",
  info: "bg-blue-500/10 text-blue-400",
  violet: "bg-violet-500/10 text-violet-400",
};

export default function StatCard({
  title,
  value,
  label,
  icon: Icon,
  tone = "info",
  danger = false,
}) {
  const resolvedTone = danger ? "danger" : tone;

  return (
    <div className="card flex items-center gap-4 p-5">
      {Icon && (
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${ICON_TONES[resolvedTone]}`}
        >
          <Icon size={20} strokeWidth={2} />
        </div>
      )}
      <div className="min-w-0">
        <div className="truncate text-xs text-slate-500">{title}</div>
        <div className="mt-1 truncate text-xl font-semibold text-white">
          {value ?? "—"}
        </div>
        {label && <div className="mt-0.5 text-xs text-slate-600">{label}</div>}
      </div>
    </div>
  );
}
