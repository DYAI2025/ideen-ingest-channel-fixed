import { useCallback, useEffect, useState } from 'react'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow'
import type { Connection, Edge, Node } from 'reactflow'
import 'reactflow/dist/style.css'
import axios from 'axios'

interface SSHGraphProps {
  apiUrl?: string
  autoRefresh?: boolean
  refreshInterval?: number
}

interface GraphData {
  nodes: Node[]
  edges: Edge[]
  metadata: {
    node_count: number
    edge_count: number
    last_updated: string
  }
}

export default function SSHGraph({ apiUrl = '/api/graph', autoRefresh = true, refreshInterval = 30000 }: SSHGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [graphData, setGraphData] = useState<GraphData | null>(null)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const loadGraphData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await axios.get(`${apiUrl}/full-graph`)
      
      if (response.data.status === 'success') {
        const data = response.data.graph
        
        // Transform nodes for ReactFlow
        const flowNodes: Node[] = data.nodes.map((node: any, index: number) => ({
          id: node.id,
          type: 'default',
          position: { 
            x: Math.cos(index * 0.5) * 200 + 400, // Circular layout
            y: Math.sin(index * 0.5) * 200 + 250 
          },
          data: { 
            label: (
              <div>
                <strong>{node.label}</strong>
                <div>{node.type}</div>
                {node.phase && <div>Phase: {node.phase}</div>}
              </div>
            ),
            originalData: node
          },
          style: {
            background: node.phase === 'seed' ? '#e8f5e9' : 
                       node.phase === 'sprout' ? '#e3f2fd' :
                       node.phase === 'growth' ? '#fff3e0' :
                       node.phase === 'flower' ? '#f3e5f5' : '#ffebee',
            border: '2px solid #4CAF50',
            borderRadius: '8px',
            padding: '10px',
            width: 180,
            fontSize: '12px'
          }
        }))
        
        // Transform edges for ReactFlow
        const flowEdges: Edge[] = data.edges.map((edge: any) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: 'smoothstep',
          animated: edge.animated || false,
          style: { stroke: '#4CAF50', strokeWidth: 2 },
          label: edge.type
        }))
        
        setNodes(flowNodes)
        setEdges(flowEdges)
        setGraphData(response.data)
      }
    } catch (err) {
      console.error('Failed to load graph data:', err)
      setError('Failed to load graph data from server')
    } finally {
      setLoading(false)
    }
  }, [apiUrl, setNodes, setEdges])

  const handleNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])

  // Auto-refresh
  useEffect(() => {
    loadGraphData()
    
    if (autoRefresh) {
      const interval = setInterval(loadGraphData, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [loadGraphData, autoRefresh, refreshInterval])

  if (loading) {
    return (
      <div className="ssh-graph-loading">
        <div className="spinner">Loading graph data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="ssh-graph-error">
        <div className="error-message">{error}</div>
        <button onClick={loadGraphData}>Retry</button>
      </div>
    )
  }

  return (
    <div className="ssh-graph-container">
      <div className="ssh-graph-header">
        <h3>🔗 GBrain Graph (SSH-Optimized)</h3>
        <div className="graph-stats">
          {graphData && (
            <>
              <span>Nodes: {graphData.metadata.node_count}</span>
              <span>Edges: {graphData.metadata.edge_count}</span>
              <span>Last updated: {graphData.metadata.last_updated}</span>
            </>
          )}
        </div>
        <button onClick={loadGraphData}>🔄 Refresh</button>
      </div>
      
      <div className="ssh-graph-viewport">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={handleNodeClick}
          fitView
          minZoom={0.2}
          maxZoom={2}
        >
          <Controls />
          <MiniMap 
            nodeColor={(node) => {
              const phase = node.data.originalData?.phase || 'seed'
              return phase === 'seed' ? '#e8f5e9' : 
                     phase === 'sprout' ? '#e3f2fd' :
                     phase === 'growth' ? '#fff3e0' :
                     phase === 'flower' ? '#f3e5f5' : '#ffebee'
            }}
          />
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
        </ReactFlow>
      </div>

      {selectedNode && (
        <div className="ssh-node-details">
          <div className="node-details-header">
            <h4>{selectedNode.data.originalData?.label || selectedNode.id}</h4>
            <button onClick={() => setSelectedNode(null)}>×</button>
          </div>
          <div className="node-details-content">
            <p><strong>Type:</strong> {selectedNode.data.originalData?.type}</p>
            <p><strong>Phase:</strong> {selectedNode.data.originalData?.phase}</p>
            <p><strong>Date:</strong> {selectedNode.data.originalData?.date}</p>
            <p><strong>ID:</strong> {selectedNode.id}</p>
          </div>
        </div>
      )}
    </div>
  )
}