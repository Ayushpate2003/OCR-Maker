import { Clock, CheckCircle, XCircle, Loader, Trash2 } from 'lucide-react'

export default function JobList({ jobs, selectedJob, onSelectJob, onDeleteJob }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'processing':
        return <Loader className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200'
      case 'failed':
        return 'bg-red-50 border-red-200'
      case 'processing':
        return 'bg-blue-50 border-blue-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  if (jobs.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Conversion Jobs</h2>
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p className="text-sm">No jobs yet</p>
          <p className="text-xs mt-1">Upload files to start converting</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Conversion Jobs ({jobs.length})
      </h2>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {jobs.map(job => (
          <div
            key={job.job_id}
            onClick={() => onSelectJob(job)}
            className={`border rounded-lg p-3 cursor-pointer transition-all ${
              selectedJob?.job_id === job.job_id
                ? 'ring-2 ring-blue-500 border-blue-500'
                : getStatusColor(job.status)
            } hover:shadow-md`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-2 flex-1 min-w-0">
                {getStatusIcon(job.status)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    Job {job.job_id.slice(0, 8)}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {job.message}
                  </p>
                  {job.status === 'processing' && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div
                          className="bg-blue-600 h-1.5 rounded-full transition-all"
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{job.progress}%</p>
                    </div>
                  )}
                  {job.files && job.files.length > 0 && (
                    <p className="text-xs text-green-600 mt-1">
                      ✓ {job.files.length} file(s) generated
                    </p>
                  )}
                  {job.error && (
                    <p className="text-xs text-red-600 mt-1">
                      ✗ {job.error}
                    </p>
                  )}
                </div>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDeleteJob(job.job_id)
                }}
                className="text-gray-400 hover:text-red-500 ml-2"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            <div className="flex items-center space-x-2 mt-2 text-xs text-gray-500">
              <span>{new Date(job.created_at).toLocaleTimeString()}</span>
              {job.uploaded_files && (
                <span>• {job.uploaded_files.length} file(s)</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
