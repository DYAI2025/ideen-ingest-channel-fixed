import { useEffect, useState } from 'react'
import axios from 'axios'
import './ObsidianGraph.css'

interface ObsidianGraphProps {
  apiUrl?: string
}

export default function ObsidianGraph({ apiUrl = 'http://localhost:3006' }: ObsidianGraphProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [graphData, setGraphData] = useState<any>(null)

  useEffect(() => {
    const loadGraph = async () => {
      try {
        setLoading(true)
        const response = await axios.get(`${apiUrl}/api/graph/files`)
        setGraphData(response.data)
      } catch (err) {
        setError('Failed to load Obsidian graph')
      } finally {
        setLoading(false)
      }
    }

    loadGraph()
  }, [apiUrl])

  if (loading) return <div className="obsidian-loading">Loading Obsidian Graph...</div>
  if (error) return <div className="obsidian-error">{error}</div>
  if (!graphData) return <div className="obsidian-error">No graph data available</div>

  return (
    <div className="obsidian-graph-container">
      <div className="obsidian-header">
        <h3>🧠 Obsidian-Style Graph</h3>
        <div className="obsidian-stats">
          <span>Nodes: {graphData.graph.nodes.length}</span>
          <span>Edges: {graphData.graph.edges.length}</span>
          <span>Ideas: {graphData.metadata.total_ideas}</span>
        </div>
      </div>
      <div className="obsidian-info">
        <p>📁 Direct file system integration with GBrain</p>
        <p>🔗 Wiki-style [[links]] support</p>
        <a href={apiUrl} target="_blank" rel="noopener noreferrer" className="open-button">
          Open Full Graph Viewer →
        </a>
      </div>
    </div>
  )
}