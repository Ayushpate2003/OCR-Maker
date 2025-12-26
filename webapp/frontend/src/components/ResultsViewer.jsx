import { useState, useEffect } from 'react'
import { Download, Eye, FileText, Code, Image as ImageIcon, X } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function ResultsViewer({ job }) {
  const [activeTab, setActiveTab] = useState('preview')
  const [fileContent, setFileContent] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (job?.files && job.files.length > 0 && !selectedFile) {
      // Auto-select first markdown/text file
      const firstTextFile = job.files.find(f => 
        f.endsWith('.md') || f.endsWith('.json') || f.endsWith('.html') || f.endsWith('.txt')
      )
      if (firstTextFile) {
        setSelectedFile(firstTextFile)
      }
    }
  }, [job])

  useEffect(() => {
    if (selectedFile && job) {
      loadFileContent(selectedFile)
    }
  }, [selectedFile, job])

  const loadFileContent = async (filePath) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/preview/${job.job_id}/${filePath}`)
      const data = await response.json()
      setFileContent(data.content)
    } catch (error) {
      console.error('Error loading file:', error)
      setFileContent(null)
    }
    setLoading(false)
  }

  const downloadFile = async (filePath) => {
    window.open(`/api/download/${job.job_id}/${filePath}`, '_blank')
  }

  const downloadAll = () => {
    if (job?.files) {
      job.files.forEach(file => downloadFile(file))
    }
  }

  if (!job) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8 border border-gray-200 h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <Eye className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-lg font-medium">No job selected</p>
          <p className="text-sm mt-2">Upload and convert files to see results here</p>
        </div>
      </div>
    )
  }

  if (job.status === 'pending' || job.status === 'processing') {
    return (
      <div className="bg-white rounded-xl shadow-md p-8 border border-gray-200 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-lg font-medium text-gray-900">{job.message}</p>
          <p className="text-sm text-gray-600 mt-2">Progress: {job.progress}%</p>
        </div>
      </div>
    )
  }

  if (job.status === 'failed') {
    return (
      <div className="bg-white rounded-xl shadow-md p-8 border border-red-200 h-full">
        <div className="text-center">
          <X className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900">Conversion Failed</p>
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 text-left">
            <p className="text-sm text-red-800 font-mono whitespace-pre-wrap">
              {job.error || 'Unknown error occurred'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  const markdownFiles = job.files?.filter(f => f.endsWith('.md')) || []
  const jsonFiles = job.files?.filter(f => f.endsWith('.json')) || []
  const htmlFiles = job.files?.filter(f => f.endsWith('.html')) || []
  const imageFiles = job.files?.filter(f => /\.(png|jpg|jpeg|gif|bmp|tiff)$/i.test(f)) || []
  const otherFiles = job.files?.filter(f => 
    !f.endsWith('.md') && !f.endsWith('.json') && !f.endsWith('.html') && 
    !/\.(png|jpg|jpeg|gif|bmp|tiff)$/i.test(f)
  ) || []

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">Conversion Results</h2>
            <p className="text-sm text-blue-100 mt-1">
              Job {job.job_id.slice(0, 8)} • {job.files?.length || 0} files
            </p>
          </div>
          <button
            onClick={downloadAll}
            className="bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 transition-colors flex items-center space-x-2 font-medium"
          >
            <Download className="w-4 h-4" />
            <span>Download All</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-gray-50">
        <div className="flex space-x-1 px-6">
          {['preview', 'files', 'images', 'raw'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 font-medium text-sm capitalize transition-colors ${
                activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6 max-h-[600px] overflow-y-auto">
        {activeTab === 'preview' && (
          <div>
            {selectedFile && fileContent ? (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {selectedFile}
                  </h3>
                  <button
                    onClick={() => downloadFile(selectedFile)}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center space-x-1"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                </div>
                {selectedFile.endsWith('.md') ? (
                  <div className="prose prose-sm max-w-none markdown-preview">
                    <ReactMarkdown>{fileContent}</ReactMarkdown>
                  </div>
                ) : selectedFile.endsWith('.json') ? (
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {JSON.stringify(JSON.parse(fileContent), null, 2)}
                  </pre>
                ) : selectedFile.endsWith('.html') ? (
                  <div 
                    className="prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={{ __html: fileContent }}
                  />
                ) : (
                  <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
                    {fileContent}
                  </pre>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>Select a file from the Files tab to preview</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'files' && (
          <div className="space-y-4">
            {markdownFiles.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Markdown Files</h3>
                <div className="space-y-2">
                  {markdownFiles.map(file => (
                    <FileItem 
                      key={file} 
                      file={file} 
                      onPreview={() => { setSelectedFile(file); setActiveTab('preview') }}
                      onDownload={() => downloadFile(file)}
                    />
                  ))}
                </div>
              </div>
            )}

            {jsonFiles.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">JSON Files</h3>
                <div className="space-y-2">
                  {jsonFiles.map(file => (
                    <FileItem 
                      key={file} 
                      file={file} 
                      onPreview={() => { setSelectedFile(file); setActiveTab('preview') }}
                      onDownload={() => downloadFile(file)}
                    />
                  ))}
                </div>
              </div>
            )}

            {htmlFiles.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">HTML Files</h3>
                <div className="space-y-2">
                  {htmlFiles.map(file => (
                    <FileItem 
                      key={file} 
                      file={file} 
                      onPreview={() => { setSelectedFile(file); setActiveTab('preview') }}
                      onDownload={() => downloadFile(file)}
                    />
                  ))}
                </div>
              </div>
            )}

            {otherFiles.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Other Files</h3>
                <div className="space-y-2">
                  {otherFiles.map(file => (
                    <FileItem 
                      key={file} 
                      file={file} 
                      onDownload={() => downloadFile(file)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'images' && (
          <div>
            {imageFiles.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {imageFiles.map(file => (
                  <div key={file} className="border border-gray-200 rounded-lg overflow-hidden">
                    <img 
                      src={`/api/download/${job.job_id}/${file}`}
                      alt={file}
                      className="w-full h-40 object-cover"
                    />
                    <div className="p-2 bg-gray-50">
                      <p className="text-xs text-gray-700 truncate">{file.split('/').pop()}</p>
                      <button
                        onClick={() => downloadFile(file)}
                        className="text-blue-600 hover:text-blue-700 text-xs mt-1"
                      >
                        Download
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <ImageIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No images extracted</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'raw' && (
          <div>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs">
              {JSON.stringify(job, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

function FileItem({ file, onPreview, onDownload }) {
  return (
    <div className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg p-3 hover:bg-gray-100 transition-colors">
      <div className="flex items-center space-x-2 flex-1 min-w-0">
        <FileText className="w-4 h-4 text-blue-500 flex-shrink-0" />
        <span className="text-sm text-gray-700 truncate">{file}</span>
      </div>
      <div className="flex items-center space-x-2 ml-2">
        {onPreview && (
          <button
            onClick={onPreview}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            <Eye className="w-4 h-4" />
          </button>
        )}
        <button
          onClick={onDownload}
          className="text-gray-600 hover:text-gray-700"
        >
          <Download className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
