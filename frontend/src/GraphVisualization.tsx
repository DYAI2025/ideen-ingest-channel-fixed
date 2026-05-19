import { useCallback, useMemo, useState } from 'react'
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

interface GraphVisualizationProps {
  ideas: any[]
  onIdeaClick?: (idea: any) => void
}

export default function GraphVisualization({ ideas, onIdeaClick }: GraphVisualizationProps) {
  const [, , onNodesChange] = useNodesState([])
  const [, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedIdea, setSelectedIdea] = useState<any>(null)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  // Convert ideas to nodes
  const ideaNodes = useMemo(() => {
    return ideas.map((idea) => ({
      id: idea.slug,
      type: 'default',
      position: { 
        x: Math.random() * 500, 
        y: Math.random() * 500 
      },
      data: { 
        label: (
          <div>
            <strong>{idea.slug}</strong>
            {idea.score && <div>Score: {idea.score.toFixed(2)}</div>}
          </div>
        ),
        idea: idea
      },
      style: {
        background: idea.phase === 'seed' ? '#e8f5e9' : 
                   idea.phase === 'sprout' ? '#e3f2fd' :
                   idea.phase === 'growth' ? '#fff3e0' :
                   idea.phase === 'flower' ? '#f3e5f5' : '#ffebee',
        border: '2px solid #4CAF50',
        borderRadius: '8px',
        padding: '10px',
        width: 200,
      }
    }))
  }, [ideas])

  // Create some example edges between related ideas
  const ideaEdges = useMemo(() => {
    const edges: Edge[] = []
    for (let i = 0; i < ideas.length - 1; i++) {
      edges.push({
        id: `e${ideas[i].slug}-${ideas[i+1].slug}`,
        source: ideas[i].slug,
        target: ideas[i+1].slug,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#4CAF50' }
      })
    }
    return edges
  }, [ideas])

  const handleNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    const idea = node.data.idea
    setSelectedIdea(idea)
    if (onIdeaClick) {
      onIdeaClick(idea)
    }
  }, [onIdeaClick])

  return (
    <div className="graph-container">
      <div className="graph-header">
        <h3>🔗 Idea Graph</h3>
        <p>Interactive visualization of idea relationships</p>
      </div>
      
      <div style={{ width: '100%', height: '500px' }}>
        <ReactFlow
          nodes={ideaNodes}
          edges={ideaEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={handleNodeClick}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>

      {selectedIdea && (
        <div className="idea-details">
          <h4>{selectedIdea.slug}</h4>
          {selectedIdea.snippet && <p>{selectedIdea.snippet}</p>}
          {selectedIdea.title && <p><strong>Title:</strong> {selectedIdea.title}</p>}
          {selectedIdea.date && <p><strong>Date:</strong> {selectedIdea.date}</p>}
          {selectedIdea.score && <p><strong>Score:</strong> {selectedIdea.score.toFixed(2)}</p>}
          <button onClick={() => setSelectedIdea(null)}>Close</button>
        </div>
      )}
    </div>
  )
}