import { Settings, Info } from 'lucide-react'

export default function ConfigPanel({ config, onChange }) {
  const ollamaModels = [
    'gemma2:2b',
    'llama3.2-vision',
    'llama3:8b',
    'mistral:7b',
    'qwen2.5:7b',
    'phi3:mini'
  ]

  const outputFormats = [
    { value: 'markdown', label: 'Markdown' },
    { value: 'json', label: 'JSON' },
    { value: 'html', label: 'HTML' },
    { value: 'chunks', label: 'Chunks' }
  ]

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <div className="flex items-center space-x-2 mb-4">
        <Settings className="w-5 h-5 text-gray-700" />
        <h2 className="text-lg font-semibold text-gray-900">Configuration</h2>
      </div>

      <div className="space-y-4">
        {/* Output Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Output Format
          </label>
          <select
            value={config.outputFormat}
            onChange={(e) => onChange({ ...config, outputFormat: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {outputFormats.map(format => (
              <option key={format.value} value={format.value}>
                {format.label}
              </option>
            ))}
          </select>
        </div>

        {/* Use LLM Toggle */}
        <div className="flex items-start space-x-3 p-4 bg-purple-50 border border-purple-200 rounded-lg">
          <input
            type="checkbox"
            id="useLlm"
            checked={config.useLlm}
            onChange={(e) => onChange({ ...config, useLlm: e.target.checked })}
            className="mt-1 w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
          />
          <div className="flex-1">
            <label htmlFor="useLlm" className="font-medium text-gray-900 cursor-pointer">
              Enable LLM Enhancement
            </label>
            <p className="text-xs text-gray-600 mt-1">
              Use Ollama for higher accuracy table extraction, inline math, and form handling
            </p>
          </div>
        </div>

        {/* Ollama Model Selection */}
        {config.useLlm && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ollama Model
            </label>
            <select
              value={config.ollamaModel}
              onChange={(e) => onChange({ ...config, ollamaModel: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {ollamaModels.map(model => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Make sure the model is pulled: <code className="bg-gray-100 px-1 rounded">ollama pull {config.ollamaModel}</code>
            </p>
          </div>
        )}

        {/* Force OCR */}
        <div className="flex items-start space-x-3">
          <input
            type="checkbox"
            id="forceOcr"
            checked={config.forceOcr}
            onChange={(e) => onChange({ ...config, forceOcr: e.target.checked })}
            className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <div className="flex-1">
            <label htmlFor="forceOcr" className="font-medium text-gray-900 cursor-pointer text-sm">
              Force OCR
            </label>
            <p className="text-xs text-gray-600 mt-1">
              Re-OCR all text, useful for scanned documents or better inline math
            </p>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start space-x-2">
          <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-blue-800">
            <p className="font-medium mb-1">Configuration Tips:</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>LLM mode provides better accuracy but is slower</li>
              <li>Ollama must be running: <code className="bg-blue-100 px-1 rounded">ollama serve</code></li>
              <li>Force OCR recommended for scanned PDFs</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
