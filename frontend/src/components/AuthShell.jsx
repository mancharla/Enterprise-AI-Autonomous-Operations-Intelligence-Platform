export default function AuthShell({ eyebrow, title, subtitle, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-base-950 px-4 py-10">
      <div
        className="pointer-events-none fixed inset-0"
        style={{
          background:
            "radial-gradient(circle at 15% 15%, rgba(59,130,246,0.12), transparent 35%), radial-gradient(circle at 85% 85%, rgba(139,92,246,0.12), transparent 35%)",
        }}
      />
      <div className="relative w-full max-w-md">
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-accent-600 to-violet-600 text-lg font-bold text-white shadow-glow">
            AI
          </div>
          <div className="text-lg font-semibold text-white">
            Enterprise AI Operations
          </div>
          <div className="mt-1 text-xs text-slate-500">{eyebrow}</div>
        </div>

        <div className="card p-8">
          <h1 className="text-xl font-semibold text-white">{title}</h1>
          {subtitle && (
            <p className="mt-1.5 text-sm text-slate-500">{subtitle}</p>
          )}
          <div className="mt-6">{children}</div>
        </div>
      </div>
    </div>
  );
}
