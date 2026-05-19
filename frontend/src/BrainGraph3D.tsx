import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import axios from 'axios'
import './BrainGraph3D.css'

interface BrainNode {
  id: string
  label: string
  type: string
  phase: string
  position: { x: number; y: number; z: number }
}

interface BrainEdge {
  id: string
  source: string
  target: string
  type: string
}

interface BrainGraph3DProps {
  apiUrl?: string
}

export default function BrainGraph3D({ apiUrl = '/api/graph' }: BrainGraph3DProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [nodes, setNodes] = useState<BrainNode[]>([])
  const [edges, setEdges] = useState<BrainEdge[]>([])
  const [selectedNode, setSelectedNode] = useState<BrainNode | null>(null)

  // Farben für Phasen
  const phaseColors = {
    seed: 0x4CAF50,    // Grün
    sprout: 0x2196F3,  // Blau
    growth: 0xFF9800,  // Orange
    flower: 0x9C27B0,  // Lila
    harvest: 0xF44336  // Rot
  }

  useEffect(() => {
    let mounted = true
    let cleanup: (() => void) | null = null

    const loadGraphData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        console.log('Loading graph data from:', apiUrl)
        const response = await axios.get(`${apiUrl}/full-graph`)
        console.log('Graph response:', response.data)
        
        if (response.data.status === 'success' && mounted) {
          const graphNodes = response.data.graph.nodes
          const graphEdges = response.data.graph.edges
          
          console.log('Nodes:', graphNodes.length, 'Edges:', graphEdges.length)

          if (graphNodes.length === 0) {
            setError('No nodes found in graph data')
            return
          }

          // 3D-Positionen in Gehirn-Struktur generieren
          const nodesWith3D = generateBrainPositions(graphNodes)
          
          setNodes(nodesWith3D)
          setEdges(graphEdges)
          
          // 3D Scene initialisieren
          cleanup = init3DScene(nodesWith3D, graphEdges)
        }
      } catch (err) {
        console.error('Failed to load graph data:', err)
        if (mounted) setError(`Failed to load graph data: ${err}`)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    loadGraphData()

    return () => {
      mounted = false
      if (cleanup) cleanup()
    }
  }, [apiUrl])

  // Gehirn-ähnliche 3D-Positionen generieren
  const generateBrainPositions = (nodes: any[]): BrainNode[] => {
    const nodesWith3D: BrainNode[] = []
    
    nodes.forEach((node, index) => {
      // Sphärische Verteilung für Gehirn-Form
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      const radius = 200 + Math.random() * 100
      
      const x = radius * Math.sin(phi) * Math.cos(theta)
      const y = radius * Math.sin(phi) * Math.sin(theta)
      const z = radius * Math.cos(phi)
      
      nodesWith3D.push({
        id: node.id,
        label: node.label,
        type: node.type,
        phase: node.phase || 'seed',
        position: { x, y, z }
      })
    })
    
    return nodesWith3D
  }

  const init3DScene = (nodes: BrainNode[], edges: BrainEdge[]) => {
    if (!containerRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0a1a) // Dunkles Gehirn-Umfeld

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    )
    camera.position.z = 500

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    containerRef.current.appendChild(renderer.domElement)

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 2)
    scene.add(ambientLight)

    const pointLight = new THREE.PointLight(0xffffff, 2, 1000)
    pointLight.position.set(0, 0, 0)
    scene.add(pointLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
    directionalLight.position.set(1, 1, 1)
    scene.add(directionalLight)

    // Gehirn-Struktur (Hemisphären)
    createBrainStructure(scene)

    // Neuronen (Nodes)
    const nodeMeshes: THREE.Mesh[] = []
    nodes.forEach(node => {
      const geometry = new THREE.SphereGeometry(15, 32, 32)
      const material = new THREE.MeshPhongMaterial({
        color: phaseColors[node.phase as keyof typeof phaseColors] || 0x4CAF50,
        emissive: phaseColors[node.phase as keyof typeof phaseColors] || 0x4CAF50,
        emissiveIntensity: 0.3,
        transparent: true,
        opacity: 0.9
      })
      
      const sphere = new THREE.Mesh(geometry, material)
      sphere.position.set(node.position.x, node.position.y, node.position.z)
      sphere.userData = { nodeId: node.id, nodeData: node }
      scene.add(sphere)
      nodeMeshes.push(sphere)

      // Glow effect
      const glowGeometry = new THREE.SphereGeometry(20, 32, 32)
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: phaseColors[node.phase as keyof typeof phaseColors] || 0x4CAF50,
        transparent: true,
        opacity: 0.2
      })
      const glow = new THREE.Mesh(glowGeometry, glowMaterial)
      glow.position.copy(sphere.position)
      scene.add(glow)
    })

    // Neural Pathways (Edges)
    edges.forEach(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source)
      const targetNode = nodes.find(n => n.id === edge.target)
      
      if (sourceNode && targetNode) {
        const points = []
        points.push(new THREE.Vector3(sourceNode.position.x, sourceNode.position.y, sourceNode.position.z))
        points.push(new THREE.Vector3(targetNode.position.x, targetNode.position.y, targetNode.position.z))
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points)
        const material = new THREE.LineBasicMaterial({
          color: 0x00ffff,
          transparent: true,
          opacity: 0.6,
          linewidth: 2
        })
        
        const line = new THREE.Line(geometry, material)
        scene.add(line)

        // Animated pulse effect
        const pulseGeometry = new THREE.BufferGeometry().setFromPoints(points)
        const pulseMaterial = new THREE.LineBasicMaterial({
          color: 0xffffff,
          transparent: true,
          opacity: 0.8
        })
        const pulseLine = new THREE.Line(pulseGeometry, pulseMaterial)
        scene.add(pulseLine)
      }
    })

    // Raycaster für Klick-Interaktion
    const raycaster = new THREE.Raycaster()
    const mouse = new THREE.Vector2()

    const onMouseClick = (event: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect()
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      raycaster.setFromCamera(mouse, camera)
      const intersects = raycaster.intersectObjects(nodeMeshes)

      if (intersects.length > 0) {
        const clickedNode = intersects[0].object.userData.nodeData
        setSelectedNode(clickedNode)
      }
    }

    renderer.domElement.addEventListener('click', onMouseClick)

    // Animation Loop
    let animationFrame: number
    const animate = () => {
      animationFrame = requestAnimationFrame(animate)
      
      // Rotation des ganzen Gehirns
      scene.rotation.y += 0.002
      
      // Pulsierender Effekt für Neuronen
      const time = Date.now() * 0.001
      nodeMeshes.forEach((mesh, i) => {
        const scale = 1 + Math.sin(time + i * 0.5) * 0.1
        mesh.scale.set(scale, scale, scale)
      })
      
      renderer.render(scene, camera)
    }
    
    animate()

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrame)
      renderer.domElement.removeEventListener('click', onMouseClick)
      renderer.dispose()
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement)
      }
    }
  }

  const createBrainStructure = (scene: THREE.Scene) => {
    // Gehirn-umriss (Ellipsoid)
    const brainGeometry = new THREE.SphereGeometry(300, 64, 64)
    const brainMaterial = new THREE.MeshBasicMaterial({
      color: 0x1a1a3a,
      transparent: true,
      opacity: 0.1,
      wireframe: true
    })
    const brainMesh = new THREE.Mesh(brainGeometry, brainMaterial)
    scene.add(brainMesh)

    // Hemisphären-Trennung
    const separatorGeometry = new THREE.PlaneGeometry(600, 600)
    const separatorMaterial = new THREE.MeshBasicMaterial({
      color: 0x333366,
      transparent: true,
      opacity: 0.1,
      side: THREE.DoubleSide
    })
    const separator = new THREE.Mesh(separatorGeometry, separatorMaterial)
    separator.rotation.y = Math.PI / 2
    scene.add(separator)
  }

  if (loading) {
    return (
      <div className="brain-graph-loading">
        <div className="brain-spinner">
          <div className="brain-icon">🧠</div>
          <div className="loading-text">Loading 3D Brain Graph...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="brain-graph-error">
        <div className="error-message">{error}</div>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    )
  }

  return (
    <div className="brain-graph-container">
      <div className="brain-graph-header">
        <h3>🧠 3D Brain Graph</h3>
        <div className="brain-stats">
          <span>Neurons: {nodes.length}</span>
          <span>Connections: {edges.length}</span>
        </div>
        <div className="phase-legend">
          <span className="legend-item seed">Seed</span>
          <span className="legend-item sprout">Sprout</span>
          <span className="legend-item growth">Growth</span>
          <span className="legend-item flower">Flower</span>
          <span className="legend-item harvest">Harvest</span>
        </div>
      </div>
      
      <div ref={containerRef} className="brain-graph-viewport" />
      
      <div className="brain-controls">
        <div className="control-hint">
          🖱️ Drag to rotate • Scroll to zoom • Click nodes for details
        </div>
      </div>

      {selectedNode && (
        <div className="brain-node-details">
          <div className="node-details-header">
            <h4>{selectedNode.label}</h4>
            <button onClick={() => setSelectedNode(null)}>×</button>
          </div>
          <div className="node-details-content">
            <p><strong>Type:</strong> {selectedNode.type}</p>
            <p><strong>Phase:</strong> {selectedNode.phase}</p>
            <p><strong>ID:</strong> {selectedNode.id}</p>
            <p><strong>Position:</strong> ({selectedNode.position.x.toFixed(0)}, {selectedNode.position.y.toFixed(0)}, {selectedNode.position.z.toFixed(0)})</p>
          </div>
        </div>
      )}
    </div>
  )
}