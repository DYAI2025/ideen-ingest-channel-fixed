import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import SimpleGraph from './SimpleGraph'
import BrainGraph3D from './BrainGraph3D'
import ObsidianGraph from './ObsidianGraph'
import './App.css'

interface FileUploadResult {
  status: string
  filename: string
  path: string
  phase: string
  timestamp: string
  auto_import: boolean
  import_result?: any
}

interface Idea {
  slug: string
  score?: number
  snippet?: string
  type?: string
  date?: string
  title?: string
}

function App() {
  const [uploadResults, setUploadResults] = useState<FileUploadResult[]>([])
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedPhase, setSelectedPhase] = useState('seed')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'simple-graph' | '3d-brain' | 'obsidian'>('list')
  const [apiError, setApiError] = useState<string | null>(null)

  const normalizeApiBaseUrl = (rawUrl?: string): string => {
    if (!rawUrl) return '/api'

    const trimmedUrl = rawUrl.replace(/\/+$/, '')
    if (!trimmedUrl) return '/api'

    return trimmedUrl.endsWith('/api') ? trimmedUrl : `${trimmedUrl}/api`
  }

  const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_URL)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setLoading(true)
    setError(null)
    
    for (const file of acceptedFiles) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('phase', selectedPhase)
      formData.append('auto_import', 'true')

      try {
        const response = await axios.post(`${API_BASE_URL}/ingest/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        
        setUploadResults(prev => [...prev, response.data])
        // Refresh ideas list after upload
        await loadIdeas()
      } catch (err) {
        setError(`Failed to upload ${file.name}: ${err}`)
      }
    }
    
    setLoading(false)
  }, [selectedPhase, API_BASE_URL])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'text/markdown': ['.md'],
      'text/plain': ['.txt'],
      'application/json': ['.json'],
      'application/x-yaml': ['.yaml', '.yml'],
    }
  })

  const loadIdeas = async () => {
    try {
      setApiError(null)
      const response = await axios.get(`${API_BASE_URL}/ideas/list`, {
        params: { phase: selectedPhase }
      })
      setIdeas(response.data.results || [])
    } catch (err) {
      console.error('Failed to load ideas:', err)
      setApiError(`Failed to connect to backend API (${API_BASE_URL}).`)
    }
  }

  const searchIdeas = async () => {
    if (!searchQuery.trim()) {
      await loadIdeas()
      return
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/ideas/search`, {
        params: { 
          query: searchQuery,
          phase: selectedPhase 
        }
      })
      setIdeas(response.data.results || [])
    } catch (err) {
      console.error('Failed to search ideas:', err)
    }
  }

  const deleteFile = async (filename: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/ingest/files/${filename}`)
      setUploadResults(prev => prev.filter(r => r.filename !== filename))
      await loadIdeas()
    } catch (err) {
      setError(`Failed to delete ${filename}: ${err}`)
    }
  }

  const loadFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ingest/files`)
      const files = response.data.files || []
      // Convert file list to upload results format
      const fileResults: FileUploadResult[] = files.map((file: any) => ({
        status: 'uploaded',
        filename: file.filename,
        path: file.path,
        phase: selectedPhase,
        timestamp: file.modified,
        auto_import: false
      }))
      setUploadResults(fileResults)
    } catch (err) {
      console.error('Failed to load files:', err)
    }
  }

  // Load initial data
  useEffect(() => {
    loadIdeas()
    loadFiles()
  }, [selectedPhase])

  return (
    <div className="app">
      <header className="header">
        <h1>🧠 Ideen Ingest Channel</h1>
        <p>SSH-zugänglicher Drag-and-Drop Eingangskanal für GBrain</p>
      </header>

      <main className="main">
        {/* Drag and Drop Zone */}
        <section className="section">
          <h2>📁 Datei-Upload</h2>
          <div className="controls">
            <label>
              Phase:
              <select 
                value={selectedPhase} 
                onChange={(e) => setSelectedPhase(e.target.value)}
              >
                <option value="seed">Seed</option>
                <option value="sprout">Sprout</option>
                <option value="growth">Growth</option>
                <option value="flower">Flower</option>
                <option value="harvest">Harvest</option>
              </select>
            </label>
          </div>
          
          <div 
            {...getRootProps()} 
            className={`dropzone ${isDragActive ? 'active' : ''}`}
          >
            <input {...getInputProps()} />
            {isDragActive ? (
              <p>📥 Drop the files here...</p>
            ) : (
              <p>🖱️ Drag & drop files here, or click to select</p>
            )}
            <p className="hint">Supported: .md, .txt, .json, .yaml, .yml</p>
          </div>

          {error && <div className="error">{error}</div>}
      {apiError && <div className="error api-error">{apiError}</div>}

          {/* Upload Results */}
          {uploadResults.length > 0 && (
            <div className="results">
              <h3>Upload Results</h3>
              <ul>
                {uploadResults.map((result, index) => (
                  <li key={index} className="result-item">
                    <span className={`status ${result.status}`}>{result.status}</span>
                    <span className="filename">{result.filename}</span>
                    {result.import_result?.status === 'success' && (
                      <span className="success">✓ Imported as {result.import_result.slug}</span>
                    )}
                    <button 
                      onClick={() => deleteFile(result.filename)}
                      className="delete-btn"
                    >
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        {/* Ideas Search and List */}
        <section className="section">
          <h2>💡 Ideen</h2>
          <div className="search-box">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search ideas..."
              onKeyPress={(e) => e.key === 'Enter' && searchIdeas()}
            />
            <button onClick={searchIdeas}>Search</button>
            <button onClick={loadIdeas}>Refresh</button>
            <div className="view-toggle">
              <button 
                className={viewMode === 'list' ? 'active' : ''}
                onClick={() => setViewMode('list')}
              >
                List
              </button>
              <button 
                className={viewMode === 'simple-graph' ? 'active' : ''}
                onClick={() => setViewMode('simple-graph')}
              >
                2D Graph
              </button>
              <button 
                className={viewMode === '3d-brain' ? 'active' : ''}
                onClick={() => setViewMode('3d-brain')}
              >
                🧠 3D Brain
              </button>
              <button 
                className={viewMode === 'obsidian' ? 'active' : ''}
                onClick={() => setViewMode('obsidian')}
              >
                📝 Obsidian
              </button>
            </div>
          </div>

          {viewMode === 'list' ? (
            ideas.length > 0 ? (
              <ul className="ideas-list">
                {ideas.map((idea, index) => (
                  <li key={index} className="idea-item">
                    <div className="idea-header">
                      <strong>{idea.slug}</strong>
                      {idea.score && <span className="score">Score: {idea.score.toFixed(2)}</span>}
                    </div>
                    {idea.snippet && <p className="snippet">{idea.snippet}</p>}
                    {idea.title && <p className="title">{idea.title}</p>}
                    {idea.date && <span className="date">{idea.date}</span>}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-ideas">No ideas found</p>
            )
          ) : viewMode === 'simple-graph' ? (
            <SimpleGraph apiUrl={`${API_BASE_URL}/graph`} />
          ) : viewMode === '3d-brain' ? (
            <BrainGraph3D apiUrl={`${API_BASE_URL}/graph`} />
          ) : (
            <ObsidianGraph />
          )}
        </section>
      </main>

      {loading && <div className="loading">Loading...</div>}
    </div>
  )
}

export default App