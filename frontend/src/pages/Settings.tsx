export default function Settings() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Integrations</h2>
        <p className="text-gray-600">Connect your Canvas, Gmail, and Gradescope accounts here.</p>
        <div className="mt-4 space-y-2">
          <button className="btn-secondary w-full">Connect Canvas</button>
          <button className="btn-secondary w-full">Connect Gmail</button>
          <button className="btn-secondary w-full">Connect Gradescope</button>
        </div>
      </div>
    </div>
  );
}
