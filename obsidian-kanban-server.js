#!/usr/bin/env node

/**
 * Obsidian-Style Kanban Graph Server
 * 
 * Kombiniert Obsidian-Graph Visualisierung mit Kanban-Funktionen
 * Arbeitet direkt mit den Obsidian-Dateien im Vault
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = 3007;
const OBSIDIAN_VAULT = '/home/dyai/obsidian-vault';

// ── Obsidian File Operations ───────────────────────────────

function getObsidianFiles() {
  const ideas = [];
  
  try {
    const phases = ['seeds', 'sprouts', 'growth', 'flowers', 'harvest'];
    
    for (const phase of phases) {
      const phaseDir = path.join(OBSIDIAN_VAULT, phase);
      if (fs.existsSync(phaseDir)) {
        const files = fs.readdirSync(phaseDir);
        
        for (const file of files) {
          if (file.endsWith('.md') && !file.startsWith('.')) {
            const filePath = path.join(phaseDir, file);
            const content = fs.readFileSync(filePath, 'utf-8');
            
            ideas.push({
              id: file.replace('.md', ''),
              title: extractTitle(content, file),
              phase: phase.replace(/s$/, ''),
              content: content,
              filePath: filePath,
              tags: extractTags(content),
              metadata: extractMetadata(content)
            });
          }
        }
      }
    }
    
    return ideas;
  } catch (error) {
    console.error('Error reading Obsidian files:', error.message);
    return [];
  }
}

function extractTitle(content, filename) {
  const titleMatch = content.match(/^#\s+(.+)$/m);
  if (titleMatch) return titleMatch[1].trim();
  
  const titleMetaMatch = content.match(/title:\s*(.+)$/m);
  if (titleMetaMatch) return titleMetaMatch[1].trim();
  
  return filename.replace('.md', '');
}

function extractTags(content) {
  const tagsMatch = content.match(/^tags:\s*\[(.+)\]/m);
  if (tagsMatch) {
    return tagsMatch[1].split(',').map(t => t.trim().replace(/"/g, ''));
  }
  return [];
}

function extractMetadata(content) {
  const metadata = {};
  const lines = content.split('\n');
  let inMetadata = false;
  
  for (const line of lines) {
    if (line.startsWith('---')) {
      inMetadata = !inMetadata;
      continue;
    }
    
    if (inMetadata) {
      const [key, ...valueParts] = line.split(':');
      if (key && valueParts.length > 0) {
        metadata[key.trim()] = valueParts.join(':').trim();
      }
    }
  }
  
  return metadata;
}

function extractLinks(content) {
  const links = [];
  const linkRegex = /\[\[([^\]]+)\](?:\|([^\]]+))?\]/g;
  let match;
  
  while ((match = linkRegex.exec(content)) !== null) {
    links.push({
      target: match[1].split('|')[0],
      text: match[2] || match[1]
    });
  }
  
  return links;
}

// ── Kanban Board State ───────────────────────────────────────

let kanbanBoard = {
  columns: [
    { id: 'backlog', title: 'Backlog', tasks: [] },
    { id: 'todo', title: 'To Do', tasks: [] },
    { id: 'in-progress', title: 'In Progress', tasks: [] },
    { id: 'review', title: 'Review', tasks: [] },
    { id: 'done', title: 'Done', tasks: [] }
  ]
};

function loadKanbanBoard() {
  const kanbanFile = path.join(OBSIDIAN_VAULT, 'kanban.json');
  if (fs.existsSync(kanbanFile)) {
    try {
      kanbanBoard = JSON.parse(fs.readFileSync(kanbanFile, 'utf-8'));
    } catch (error) {
      console.error('Error loading kanban board:', error.message);
    }
  }
}

function saveKanbanBoard() {
  const kanbanFile = path.join(OBSIDIAN_VAULT, 'kanban.json');
  fs.writeFileSync(kanbanFile, JSON.stringify(kanbanBoard, null, 2));
}

// ── HTTP Server ─────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.end();
  }
  
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const path = url.pathname;
  
  // API Endpoints
  if (path === '/api/files') {
    const ideas = getObsidianFiles();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'success',
      ideas: ideas,
      count: ideas.length
    }));
  } else if (path === '/api/graph') {
    const ideas = getObsidianFiles();
    const nodes = ideas.map(idea => ({
      id: idea.id,
      label: idea.title,
      phase: idea.phase,
      tags: idea.tags
    }));
    
    const edges = [];
    ideas.forEach(idea => {
      const links = extractLinks(idea.content);
      links.forEach(link => {
        const targetExists = nodes.some(n => n.id === link.target);
        if (targetExists && idea.id !== link.target) {
          edges.push({
            id: `${idea.id}-${link.target}`,
            source: idea.id,
            target: link.target,
            type: 'wiki-link'
          });
        }
      });
    });
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'success',
      graph: { nodes, edges },
      metadata: {
        node_count: nodes.length,
        edge_count: edges.length
      }
    }));
  } else if (path === '/api/kanban') {
    loadKanbanBoard();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'success',
      board: kanbanBoard
    }));
  } else if (path === '/api/kanban' && req.method === 'POST') {
    const body = await parseBody(req);
    kanbanBoard = body.board || kanbanBoard;
    saveKanbanBoard();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'success', board: kanbanBoard }));
  } else if (path.startsWith('/api/kanban/move')) {
    const parts = path.split('/');
    const taskId = parts[3];
    const targetColumn = parts[4];
    
    // Move task between columns
    for (const col of kanbanBoard.columns) {
      const taskIndex = col.tasks.findIndex(t => t.id === taskId);
      if (taskIndex !== -1) {
        const [task] = col.tasks.splice(taskIndex, 1);
        const targetCol = kanbanBoard.columns.find(c => c.id === targetColumn);
        if (targetCol) {
          task.movedAt = new Date().toISOString();
          targetCol.tasks.push(task);
        }
        break;
      }
    }
    
    saveKanbanBoard();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'success', board: kanbanBoard }));
  } else if (path.startsWith('/api/files/') && path.endsWith('/open')) {
    // Open Obsidian file externally
    const filename = path.split('/').slice(-2, -1)[0];
    const filePath = path.join(OBSIDIAN_VAULT, filename);
    
    if (fs.existsSync(filePath)) {
      // Try to open with default app
      const { spawn } = require('child_process');
      const opener = process.platform === 'darwin' ? 'open' : 
                     process.platform === 'win32' ? 'start' : 'xdg-open';
      
      spawn(opener, [filePath], { detached: true });
      
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'success', message: 'Opening file...' }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'File not found' }));
    }
  } else if (path === '/') {
    // Serve HTML interface
    const html = `
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obsidian Kanban Graph</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * { box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e2e8f0;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #8b5cf6;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #94a3b8;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 10px 20px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            cursor: pointer;
            color: #cbd5e1;
            transition: all 0.2s;
        }
        
        .tab.active {
            background: #8b5cf6;
            border-color: #8b5cf6;
            color: white;
        }
        
        .tab:hover {
            background: #334155;
        }
        
        .view {
            display: none;
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #334155;
            min-height: 600px;
        }
        
        .view.active {
            display: block;
        }
        
        /* Graph Styles */
        .graph-container {
            height: 500px;
            position: relative;
        }
        
        .node {
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .node:hover {
            filter: brightness(1.3);
        }
        
        .link {
            stroke: #64748b;
            stroke-opacity: 0.6;
        }
        
        .node-label {
            font-size: 11px;
            fill: #e2e8f0;
            pointer-events: none;
        }
        
        /* Kanban Styles */
        .kanban-board {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 15px;
            min-height: 500px;
        }
        
        .kanban-column {
            background: #0f172a;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #1e293b;
        }
        
        .kanban-column-header {
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
            color: #8b5cf6;
        }
        
        .kanban-tasks {
            min-height: 300px;
        }
        
        .kanban-task {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            cursor: grab;
            transition: all 0.2s;
        }
        
        .kanban-task:hover {
            border-color: #8b5cf6;
            transform: translateY(-2px);
        }
        
        .kanban-task-title {
            font-weight: 500;
            margin-bottom: 5px;
            color: #f1f5f9;
        }
        
        .kanban-task-phase {
            font-size: 12px;
            color: #94a3b8;
            background: #0f172a;
            padding: 3px 8px;
            border-radius: 12px;
            display: inline-block;
        }
        
        .kanban-task-actions {
            margin-top: 8px;
            display: flex;
            gap: 8px;
        }
        
        .kanban-btn {
            padding: 4px 8px;
            background: #334155;
            border: 1px solid #475569;
            border-radius: 4px;
            color: #cbd5e1;
            font-size: 11px;
            cursor: pointer;
        }
        
        .kanban-btn:hover {
            background: #475569;
        }
        
        .stats {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 20px;
            color: #94a3b8;
            font-size: 14px;
        }
        
        .controls {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: #1e293b;
            border-radius: 8px;
        }
        
        .btn {
            padding: 10px 20px;
            background: #8b5cf6;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin: 0 5px;
        }
        
        .btn:hover {
            background: #7c3aed;
        }
        
        .phase-legend {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: #94a3b8;
        }
        
        .legend-color {
            width: 14px;
            height: 14px;
            border-radius: 50%;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Obsidian Kanban Graph</h1>
            <p>GBrain-Ideen mit Graph-Visualisierung und Kanban-Board</p>
        </div>
        
        <div class="stats">
            <span id="total-ideas">Ideas: 0</span>
            <span id="phase-breakdown">Phases: -</span>
        </div>
        
        <div class="phase-legend">
            <div class="legend-item"><div class="legend-color" style="background: #4CAF50;"></div> Seed</div>
            <div class="legend-item"><div class="legend-color" style="background: #2196F3;"></div> Sprout</div>
            <div class="legend-item"><div class="legend-color" style="background: #FF9800;"></div> Growth</div>
            <div class="legend-item"><div class="legend-color" style="background: #9C27B0;"></div> Flower</div>
            <div class="legend-item"><div class="legend-color" style="background: #F44336;"></div> Harvest</div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('graph')">🔗 Graph</div>
            <div class="tab" onclick="switchTab('kanban')">📋 Kanban</div>
            <div class="tab" onclick="switchTab('files')">📁 Files</div>
        </div>
        
        <div id="graph-view" class="view active">
            <div class="graph-container" id="graph"></div>
        </div>
        
        <div id="kanban-view" class="view">
            <div class="kanban-board" id="kanban-board"></div>
        </div>
        
        <div id="files-view" class="view">
            <div id="files-list"></div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshAll()">🔄 Refresh All</button>
            <button class="btn" onclick="openObsidian()">🧠 Open Obsidian</button>
        </div>
    </div>
    
    <script>
        let currentTab = 'graph';
        let kanbanBoard = { columns: [] };
        let allIdeas = [];
        
        const phaseColors = {
            seed: '#4CAF50',
            sprout: '#2196F3',
            growth: '#FF9800',
            flower: '#9C27B0',
            harvest: '#F44336'
        };
        
        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-view').classList.add('active');
            
            if (tab === 'graph') renderGraph();
            if (tab === 'kanban') renderKanban();
            if (tab === 'files') renderFiles();
        }
        
        async function refreshAll() {
            await loadIdeas();
            if (currentTab === 'graph') renderGraph();
            if (currentTab === 'kanban') renderKanban();
            if (currentTab === 'files') renderFiles();
        }
        
        async function loadIdeas() {
            const response = await axios.get('/api/files');
            allIdeas = response.data.ideas;
            
            document.getElementById('total-ideas').textContent = \`Ideas: \${allIdeas.length}\`;
            
            const phaseCount = {};
            allIdeas.forEach(idea => {
                phaseCount[idea.phase] = (phaseCount[idea.phase] || 0) + 1;
            });
            
            document.getElementById('phase-breakdown').textContent = 
                Object.entries(phaseCount).map(([phase, count]) => \`\${phase}: \${count}\`).join(', ');
        }
        
        function renderGraph() {
            const container = document.getElementById('graph');
            container.innerHTML = '';
            
            const width = container.clientWidth;
            const height = 500;
            
            // Create nodes from ideas
            const nodes = allIdeas.map(idea => ({
              id: idea.id,
              label: idea.title,
              phase: idea.phase,
              tags: idea.tags
            }));
            
            // Extract links
            const edges = [];
            allIdeas.forEach(idea => {
              const content = idea.content;
              const linkRegex = /\\[\\[([^\\]]+)\\](?:\\|([^\\]]+))?\\]/g;
              let match;
              
              while ((match = linkRegex.exec(content)) !== null) {
                const target = match[1].split('|')[0];
                const targetExists = nodes.some(n => n.id === target);
                if (targetExists && idea.id !== target) {
                  edges.push({
                    id: \`\${idea.id}-\${target}\`,
                    source: idea.id,
                    target: target,
                    type: 'wiki-link'
                  });
                }
              }
            });
            
            // Fallback sequential edges
            if (edges.length === 0 && nodes.length > 1) {
              for (let i = 0; i < nodes.length - 1; i++) {
                edges.push({
                  id: \`seq-\${nodes[i].id}-\${nodes[i + 1].id}\`,
                  source: nodes[i].id,
                  target: nodes[i + 1].id,
                  type: 'sequence'
                });
              }
            }
            
            // D3.js Graph
            const svg = d3.select('#graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const g = svg.append('g');
            
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on('zoom', (event) => {
                    g.attr('transform', event.transform);
                });
            
            svg.call(zoom);
            
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(30));
            
            const link = g.append('g')
                .selectAll('line')
                .data(edges)
                .join('line')
                .attr('class', 'link')
                .attr('stroke-width', 2);
            
            const node = g.append('g')
                .selectAll('circle')
                .data(nodes)
                .join('circle')
                .attr('class', 'node')
                .attr('r', 20)
                .attr('fill', d => phaseColors[d.phase] || '#4CAF50')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended))
                .on('click', (event, d) => showNodeDetails(d));
            
            const labels = g.append('g')
                .selectAll('text')
                .data(nodes)
                .join('text')
                .attr('class', 'node-label')
                .text(d => d.label)
                .attr('text-anchor', 'middle')
                .attr('dy', 35);
            
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d.target.y);
                
                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                labels
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            });
        }
        
        function renderKanban() {
            axios.get('/api/kanban').then(response => {
                kanbanBoard = response.data.board;
                updateKanbanUI();
            });
        }
        
        function updateKanbanUI() {
            const board = document.getElementById('kanban-board');
            board.innerHTML = '';
            
            kanbanBoard.columns.forEach(column => {
                const colDiv = document.createElement('div');
                colDiv.className = 'kanban-column';
                colDiv.innerHTML = \`
                    <div class="kanban-column-header">\${column.title} (\${column.tasks.length})</div>
                    <div class="kanban-tasks" data-column="\${column.id}"></div>
                \`;
                
                const tasksContainer = colDiv.querySelector('.kanban-tasks');
                
                column.tasks.forEach(task => {
                    const taskDiv = document.createElement('div');
                    taskDiv.className = 'kanban-task';
                    taskDiv.draggable = true;
                    taskDiv.innerHTML = \`
                        <div class="kanban-task-title">\${task.title}</div>
                        <div class="kanban-task-phase">\${task.phase || 'No phase'}</div>
                        <div class="kanban-task-actions">
                            <button class="kanban-btn" onclick="moveTask('\${task.id}', '\${column.id}')">Move →</button>
                        </div>
                    \`;
                    
                    tasksContainer.appendChild(taskDiv);
                });
                
                board.appendChild(colDiv);
            });
        }
        
        function renderFiles() {
            const list = document.getElementById('files-list');
            list.innerHTML = '';
            
            allIdeas.forEach(idea => {
              const fileDiv = document.createElement('div');
              fileDiv.className = 'kanban-task';
              fileDiv.innerHTML = \`
                <div class="kanban-task-title">\${idea.title}</div>
                <div class="kanban-task-phase">\${idea.phase}</div>
                <div class="kanban-task-actions">
                  <button class="kanban-btn" onclick="openFile('\${idea.id}')">📄 Open</button>
                  <button class="kanban-btn" onclick="addToKanban('\${idea.id}')">📋 Add to Kanban</button>
                </div>
              \`;
              list.appendChild(fileDiv);
            });
        }
        
        function moveTask(taskId, fromColumn) {
            const columns = kanbanBoard.columns;
            const currentColIndex = columns.findIndex(c => c.id === fromColumn);
            const nextColIndex = (currentColIndex + 1) % columns.length;
            const targetColumn = columns[nextColIndex].id;
            
            axios.post(\`/api/kanban/move/\${taskId}/\${targetColumn}\`)
                .then(() => {
                    renderKanban();
                });
        }
        
        async function openFile(fileId) {
            const extension = fileId.endsWith('.md') ? '' : '.md';
            await axios.get(\`/api/files/\${fileId}/open\`);
        }
        
        function addToKanban(fileId) {
            const idea = allIdeas.find(i => i.id === fileId);
            if (idea) {
                const newTask = {
                    id: 'task-' + Date.now(),
                    title: idea.title,
                    phase: idea.phase,
                    description: idea.content.substring(0, 200),
                    source: idea.id
                };
                
                kanbanBoard.columns[0].tasks.push(newTask);
                
                axios.post('/api/kanban', { board: kanbanBoard })
                    .then(() => {
                        renderKanban();
                    });
            }
        }
        
        function openObsidian() {
            window.open('obsidian:///home/dyai/obsidian-vault', '_blank');
        }
        
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Initialize
        loadIdeas().then(() => {
            renderGraph();
        });
    </script>
</body>
</html>
    `;
    
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🧠 Obsidian Kanban Graph Server running on http://localhost:${PORT}`);
  console.log(`📁 Obsidian Vault: ${OBSIDIAN_VAULT}`);
  console.log(`🌐 Open http://localhost:${PORT} for the interface`);
});