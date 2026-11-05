export default function Field({ label, error, id, children, ...props }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className="field-row">
        <input id={id} aria-invalid={!!error} aria-describedby={error ? `${id}-e` : undefined} {...props} />
        {children}
      </div>
      {error && <small id={`${id}-e`} className="err" role="alert">{error}</small>}
    </div>
  )
}
