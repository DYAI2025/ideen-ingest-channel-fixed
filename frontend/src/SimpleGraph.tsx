import { useEffect, useState } from 'react'
import axios from 'axios'

interface SimpleGraphProps {
  apiUrl?: string
}

interface GraphNode {
  id: string
  label: string
  type: string
  phase: string
  date: string
}

interface GraphEdge {
  id: string
  source: string
  target: string
  type: string
}

export default function SimpleGraph({ apiUrl = '/api/graph' }: SimpleGraphProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)

  const loadGraphData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await axios.get(`${apiUrl}/full-graph`)
      
      if (response.data.status === 'success') {
        const data = response.data.graph
        setNodes(data.nodes)
        setEdges(data.edges)
      }
    } catch (err) {
      console.error('Failed to load graph data:', err)
      setError('Failed to load graph data from server')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadGraphData()
  }, [apiUrl])

  if (loading) {
    return (
      <div className="simple-graph-loading">
        <div className="spinner">Loading graph data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="simple-graph-error">
        <div className="error-message">{error}</div>
        <button onClick={loadGraphData}>Retry</button>
      </div>
    )
  }

  return (
    <div className="simple-graph-container">
      <div className="simple-graph-header">
        <h3>🔗 GBrain Graph (Simple Version)</h3>
        <div className="graph-stats">
          <span>Nodes: {nodes.length}</span>
          <span>Edges: {edges.length}</span>
        </div>
        <button onClick={loadGraphData}>🔄 Refresh</button>
      </div>
      
      <div className="simple-graph-content">
        <div className="nodes-list">
          <h4>Nodes (Ideas)</h4>
          <ul>
            {nodes.map((node) => (
              <li 
                key={node.id} 
                className={`node-item phase-${node.phase}`}
                onClick={() => setSelectedNode(node)}
              >
                <strong>{node.label}</strong>
                <span className="node-type">{node.type}</span>
                <span className="node-phase">{node.phase}</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="edges-list">
          <h4>Edges (Connections)</h4>
          <ul>
            {edges.map((edge) => (
              <li key={edge.id} className="edge-item">
                <span className="edge-source">{edge.source}</span>
                <span className="edge-arrow">→</span>
                <span className="edge-target">{edge.target}</span>
                <span className="edge-type">{edge.type}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {selectedNode && (
        <div className="simple-node-details">
          <div className="node-details-header">
            <h4>{selectedNode.label}</h4>
            <button onClick={() => setSelectedNode(null)}>×</button>
          </div>
          <div className="node-details-content">
            <p><strong>Type:</strong> {selectedNode.type}</p>
            <p><strong>Phase:</strong> {selectedNode.phase}</p>
            <p><strong>Date:</strong> {selectedNode.date}</p>
            <p><strong>ID:</strong> {selectedNode.id}</p>
          </div>
        </div>
      )}
    </div>
  )
}