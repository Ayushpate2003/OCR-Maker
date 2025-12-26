import { useState, useEffect } from 'react'
import FileUpload from './components/FileUpload'
import ConfigPanel from './components/ConfigPanel'
import JobList from './components/JobList'
import ResultsViewer from './components/ResultsViewer'
import { FileText } from 'lucide-react'

function App() {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [config, setConfig] = useState({
    useLlm: false,
    ollamaModel: 'gemma2:2b',
    outputFormat: 'markdown',
    forceOcr: false
  })

  // Poll for job updates
  useEffect(() => {
    const interval = setInterval(() => {
      jobs.forEach(job => {
        if (job.status === 'pending' || job.status === 'processing') {
          fetchJobStatus(job.job_id)
        }
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [jobs])

  const fetchJobStatus = async (jobId) => {
    try {
      const response = await fetch(`/api/jobs/${jobId}`)
      const data = await response.json()
      
      setJobs(prev => prev.map(job => 
        job.job_id === jobId ? data : job
      ))

      if (selectedJob?.job_id === jobId) {
        setSelectedJob(data)
      }
    } catch (error) {
      console.error('Error fetching job status:', error)
    }
  }

  const handleUpload = async (files) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('use_llm', config.useLlm)
    formData.append('ollama_model', config.ollamaModel)
    formData.append('output_format', config.outputFormat)
    formData.append('force_ocr', config.forceOcr)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      // Safely parse JSON (even for error responses)
      const tryParseJson = async (resp) => {
        const ct = resp.headers.get('content-type') || ''
        if (!ct.includes('application/json')) {
          const text = await resp.text()
          throw new Error(text || `HTTP ${resp.status}`)
        }
        return await resp.json()
      }

      if (!response.ok) {
        try {
          const err = await tryParseJson(response)
          throw new Error(err.detail || JSON.stringify(err))
        } catch (e) {
          throw e
        }
      }

      const data = await tryParseJson(response)
      
      // Fetch initial job status
      const jobResponse = await fetch(`/api/jobs/${data.job_id}`)
      const jobData = await jobResponse.json()
      
      setJobs(prev => [jobData, ...prev])
      setSelectedJob(jobData)
      
      return { success: true }
    } catch (error) {
      console.error('Upload error:', error)
      return { success: false, error: (error && error.message) ? error.message : 'Upload failed' }
    }
  }

  const handleDeleteJob = async (jobId) => {
    try {
      await fetch(`/api/jobs/${jobId}`, { method: 'DELETE' })
      setJobs(prev => prev.filter(job => job.job_id !== jobId))
      if (selectedJob?.job_id === jobId) {
        setSelectedJob(null)
      }
    } catch (error) {
      console.error('Error deleting job:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Marker Converter</h1>
                <p className="text-sm text-gray-600">Transform documents to Markdown with AI</p>
              </div>
            </div>

          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload & Config */}
          <div className="lg:col-span-1 space-y-6">
            <FileUpload onUpload={handleUpload} />
            <ConfigPanel config={config} onChange={setConfig} />
            <JobList 
              jobs={jobs} 
              selectedJob={selectedJob}
              onSelectJob={setSelectedJob}
              onDeleteJob={handleDeleteJob}
            />
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            <ResultsViewer job={selectedJob} />
          </div>
        </div>
      </main>


    </div>
  )
}

export default App
