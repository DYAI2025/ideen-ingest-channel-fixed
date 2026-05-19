import { useState, useEffect } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import axios from 'axios'
import './KanbanBoard.css'

interface Task {
  id: string
  title: string
  description: string | null
  phase: string
  tags: string[]
  status: string
  createdAt: string | null
  updatedAt: string | null
}

interface Column {
  id: string
  title: string
  tasks: Task[]
}

const phaseColors = {
  seed: '#4CAF50',
  sprout: '#2196F3',
  growth: '#FF9800',
  flower: '#9C27B0',
  harvest: '#F44336'
}

const initialColumns: Column[] = [
  {
    id: 'backlog',
    title: '📋 Backlog',
    tasks: []
  },
  {
    id: 'todo',
    title: '📝 To Do',
    tasks: []
  },
  {
    id: 'in-progress',
    title: '🚀 In Progress',
    tasks: []
  },
  {
    id: 'review',
    title: '👀 Review',
    tasks: []
  },
  {
    id: 'done',
    title: '✅ Done',
    tasks: []
  }
]

function KanbanBoard() {
  const [columns, setColumns] = useState<Column[]>(initialColumns)
  const [selectedPhase, setSelectedPhase] = useState<string>('all')
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)

  // Load kanban data on mount
  useEffect(() => {
    loadKanbanData()
  }, [])

  const loadKanbanData = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/kanban/board')
      if (response.data.status === 'success') {
        // Transform backend data to frontend format
        const transformedColumns = response.data.board.columns.map((col: any) => ({
          id: col.id,
          title: col.title,
          tasks: col.tasks.map((task: any) => ({
            id: task.id,
            title: task.title,
            description: task.description,
            phase: task.phase,
            tags: task.tags,
            status: task.status,
            createdAt: task.created_at,
            updatedAt: task.updated_at
          }))
        }))
        setColumns(transformedColumns)
      }
    } catch (error) {
      console.error('Failed to load kanban data:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveKanbanData = async (newColumns: Column[]) => {
    try {
      // Transform to match backend schema
      const boardData = {
        columns: newColumns.map(col => ({
          id: col.id,
          title: col.title,
          tasks: col.tasks.map(task => ({
            id: task.id,
            title: task.title,
            description: task.description || null,
            phase: task.phase,
            tags: task.tags || [],
            status: task.status,
            created_at: task.createdAt || null,
            updated_at: task.updatedAt || null
          }))
        }))
      }
      
      await axios.post('/api/kanban/board', boardData)
    } catch (error) {
      console.error('Failed to save kanban data:', error)
    }
  }

  const onDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result

    if (!destination) return

    if (destination.droppableId === source.droppableId && destination.index === source.index) {
      return
    }

    const sourceColumn = columns.find(col => col.id === source.droppableId)
    const destColumn = columns.find(col => col.id === destination.droppableId)

    if (!sourceColumn || !destColumn) return

    const task = sourceColumn.tasks.find(task => task.id === draggableId)
    if (!task) return

    // Remove from source
    const newSourceTasks = [...sourceColumn.tasks]
    newSourceTasks.splice(source.index, 1)

    // Add to destination
    const newDestTasks = [...destColumn.tasks]
    newDestTasks.splice(destination.index, 0, { 
      ...task, 
      status: destination.droppableId,
      updatedAt: new Date().toISOString()
    })

    const newColumns = columns.map(col => {
      if (col.id === source.droppableId) {
        return { ...col, tasks: newSourceTasks }
      }
      if (col.id === destination.droppableId) {
        return { ...col, tasks: newDestTasks }
      }
      return col
    })

    setColumns(newColumns)
    saveKanbanData(newColumns)
  }

  const addTask = async (title: string, phase: string) => {
    try {
      const newTask = {
        id: `task-${Date.now()}`,
        title,
        description: null,
        phase,
        tags: [phase],
        status: 'backlog',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      await axios.post('/api/kanban/task', newTask)
      loadKanbanData()
    } catch (error) {
      console.error('Failed to add task:', error)
    }
  }

  const deleteTask = async (taskId: string) => {
    try {
      await axios.delete(`/api/kanban/task/${taskId}`)
      loadKanbanData()
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  const syncGBrainToKanban = async () => {
    try {
      setSyncing(true)
      const response = await axios.post('/api/sync/kanban')
      if (response.data.status === 'success') {
        loadKanbanData()
        alert('✅ GBrain → Kanban sync completed!')
      } else {
        alert(`❌ Sync failed: ${response.data.message}`)
      }
    } catch (error) {
      console.error('Failed to sync:', error)
      alert('❌ Failed to sync GBrain to Kanban')
    } finally {
      setSyncing(false)
    }
  }

  const filteredTasks = (tasks: Task[]) => {
    if (selectedPhase === 'all') return tasks
    return tasks.filter(task => task.phase === selectedPhase)
  }

  return (
    <div className="kanban-board">
      <div className="kanban-controls">
        <h3>📋 Kanban Board</h3>
        <select 
          value={selectedPhase} 
          onChange={(e) => setSelectedPhase(e.target.value)}
          className="phase-filter"
        >
          <option value="all">All Phases</option>
          <option value="seed">Seed</option>
          <option value="sprout">Sprout</option>
          <option value="growth">Growth</option>
          <option value="flower">Flower</option>
          <option value="harvest">Harvest</option>
        </select>
        <button 
          onClick={() => {
            const title = prompt('Task title:')
            if (title) {
              const phase = prompt('Phase (seed/sprout/growth/flower/harvest):', 'seed')
              if (phase && ['seed', 'sprout', 'growth', 'flower', 'harvest'].includes(phase)) {
                addTask(title, phase)
              }
            }
          }}
          className="add-task-btn"
          disabled={syncing}
        >
          + Add Task
        </button>
        <button 
          onClick={syncGBrainToKanban}
          className="sync-btn"
          disabled={syncing}
        >
          {syncing ? '🔄 Syncing...' : '🔄 Sync GBrain'}
        </button>
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="kanban-columns">
          {columns.map(column => (
            <div key={column.id} className="kanban-column">
              <div className="column-header">
                <h4>{column.title}</h4>
                <span className="task-count">{filteredTasks(column.tasks).length}</span>
              </div>
              
              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className={`task-list ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
                  >
                    {filteredTasks(column.tasks).map((task, index) => (
                      <Draggable key={task.id} draggableId={task.id} index={index}>
                        {(provided, snapshot) => (
                          <div
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            ref={provided.innerRef}
                            className={`task-card ${snapshot.isDragging ? 'dragging' : ''}`}
                            style={{
                              borderLeft: `4px solid ${phaseColors[task.phase as keyof typeof phaseColors] || '#999'}`
                            }}
                          >
                            <div className="task-content">
                              <h5>{task.title}</h5>
                              {task.description && <p>{task.description}</p>}
                              <div className="task-meta">
                                {task.phase && (
                                  <span className="phase-tag" style={{ backgroundColor: phaseColors[task.phase as keyof typeof phaseColors] }}>
                                    {task.phase}
                                  </span>
                                )}
                                {task.tags?.map(tag => (
                                  <span key={tag} className="tag">{tag}</span>
                                ))}
                              </div>
                            </div>
                            <button 
                              onClick={() => deleteTask(task.id)}
                              className="delete-btn"
                            >
                              ×
                            </button>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  )
}

export default KanbanBoard