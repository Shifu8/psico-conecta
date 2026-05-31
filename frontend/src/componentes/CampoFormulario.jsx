export default function CampoFormulario({ label, error, children }) {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>
      {children}
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}
