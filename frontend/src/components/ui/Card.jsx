export default function Card({
  title,
  description,
  action,
  className = "",
  bodyClassName = "",
  children,
}) {
  return (
    <div className={`card p-6 ${className}`}>
      {(title || action) && (
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            {title && (
              <h3 className="text-sm font-semibold text-slate-100">
                {title}
              </h3>
            )}
            {description && (
              <p className="mt-1 text-xs text-slate-500">{description}</p>
            )}
          </div>
          {action}
        </div>
      )}
      <div className={bodyClassName}>{children}</div>
    </div>
  );
}
