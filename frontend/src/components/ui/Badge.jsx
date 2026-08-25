const TONES = {
  neutral: "bg-slate-500/10 text-slate-300 border-slate-500/20",
  success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  info: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  danger: "bg-red-500/10 text-red-400 border-red-500/20",
  violet: "bg-violet-500/10 text-violet-400 border-violet-500/20",
};

const SEVERITY_TONE = {
  critical: "danger",
  high: "warning",
  medium: "info",
  low: "neutral",
  active: "success",
  open: "warning",
  acknowledged: "info",
  resolved: "success",
};

export function toneForStatus(value) {
  if (!value) return "neutral";
  return SEVERITY_TONE[String(value).toLowerCase()] || "neutral";
}

export default function Badge({ children, tone = "neutral", className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${TONES[tone] || TONES.neutral} ${className}`}
    >
      {children}
    </span>
  );
}
