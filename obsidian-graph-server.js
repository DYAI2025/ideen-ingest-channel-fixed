#!/usr/bin/env node

/**
 * Obsidian-Style Graph Viewer for GBrain
 * 
 * Liest GBrain Markdown-Dateien und erstellt eine Obsidian-ähnliche Graph-Visualisierung
 * Verwendet D3.js für Force-Directed Graph
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = 3006;
const GBBRAIN_SOURCE = path.join(process.env.HOME, 'ideen-growth-system');
const GRAPH_API_URL = 'http://localhost:8001/api/graph/full-graph';

// ── GBrain File System Integration ───────────────────────

function readGBrainFiles() {
  const ideas = [];
  
  try {
    const phases = ['seeds', 'sprouts', 'growth', 'flowers', 'harvest'];
    
    for (const phase of phases) {
      const phaseDir = path.join(GBBRAIN_SOURCE, phase);
      if (fs.existsSync(phaseDir)) {
        const files = fs.readdirSync(phaseDir);
        
        for (const file of files) {
          if (file.endsWith('.md') && !file.startsWith('.')) {
            const filePath = path.join(phaseDir, file);
            const content = fs.readFileSync(filePath, 'utf-8');
            
            // Parse frontmatter and content
            const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
            const frontmatter = frontmatterMatch ? frontmatterMatch[1] : '';
            const bodyContent = frontmatterMatch ? content.replace(/^---\n[\s\S]*?\n---\n/, '') : content;
            
            // Parse YAML frontmatter
            const metadata = {};
            frontmatter.split('\n').forEach(line => {
              const [key, ...valueParts] = line.split(':');
              if (key && valueParts.length > 0) {
                metadata[key.trim()] = valueParts.join(':').trim();
              }
            });
            
            ideas.push({
              id: file.replace('.md', ''),
              title: metadata.title || file.replace('.md', ''),
              phase: phase.replace(/s$/, ''), // seeds -> seed, etc.
              content: bodyContent,
              metadata: metadata,
              filePath: filePath,
              createdAt: metadata.date || new Date().toISOString()
            });
          }
        }
      }
    }
    
    return ideas;
  } catch (error) {
    console.error('Error reading GBrain files:', error.message);
    return [];
  }
}

// ── Link Detection (Wiki-style links) ───────────────────────

function extractLinks(content) {
  const links = [];
  // Match [[link]] or [[link|text]] patterns
  const linkRegex = /\[\[([^\]]+)\](?:\|([^\]]+))?\]/g;
  let match;
  
  while ((match = linkRegex.exec(content)) !== null) {
    links.push({
      target: match[1].split('|')[0], // Handle [[target|text]] format
      text: match[2] || match[1]
    });
  }
  
  return links;
}

function buildGraphFromFiles(ideas) {
  const nodes = ideas.map(idea => ({
    id: idea.id,
    label: idea.title,
    phase: idea.phase,
    content: idea.content.substring(0, 200), // Preview
    file: idea.filePath
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
  
  // Fallback: Create sequential edges if no wiki links found
  if (edges.length === 0 && nodes.length > 1) {
    for (let i = 0; i < nodes.length - 1; i++) {
      edges.push({
        id: `seq-${nodes[i].id}-${nodes[i + 1].id}`,
        source: nodes[i].id,
        target: nodes[i + 1].id,
        type: 'sequence'
      });
    }
  }
  
  return { nodes, edges };
}

// ── HTTP Server ─────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.end();
  }
  
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const path = url.pathname;
  
  if (path === '/api/graph/files') {
    const ideas = readGBrainFiles();
    const graph = buildGraphFromFiles(ideas);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'success',
      graph: graph,
      metadata: {
        node_count: graph.nodes.length,
        edge_count: graph.edges.length,
        source: 'gbrain-files',
        total_ideas: ideas.length
      }
    }));
  } else if (path === '/api/ideas') {
    const ideas = readGBrainFiles();
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'success',
      ideas: ideas,
      count: ideas.length
    }));
  } else if (path === '/api/ideas/:id') {
    const ideaId = path.split('/').pop();
    const ideas = readGBrainFiles();
    const idea = ideas.find(i => i.id === ideaId);
    
    if (idea) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'success',
        idea: idea
      }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Idea not found' }));
    }
  } else if (path === '/') {
    // Serve HTML interface
    const html = `
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obsidian-Style GBrain Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            color: #e0e0e0;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #7c3aed;
            margin-bottom: 10px;
        }
        
        .graph-container {
            background: #2d2d2d;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        
        .stats {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 20px;
            color: #a0a0a0;
        }
        
        .node {
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .node:hover {
            filter: brightness(1.3);
        }
        
        .link {
            stroke: #666;
            stroke-opacity: 0.6;
        }
        
        .node-label {
            font-size: 12px;
            fill: #e0e0e0;
            pointer-events: none;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        }
        
        .phase-legend {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }
        
        .controls {
            text-align: center;
            margin-top: 20px;
            color: #a0a0a0;
        }
        
        button {
            background: #7c3aed;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin: 0 5px;
        }
        
        button:hover {
            background: #6d28d9;
        }
        
        .node-details {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #2d2d2d;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            z-index: 1000;
            max-width: 500px;
            width: 90%;
            border: 2px solid #7c3aed;
        }
        
        .node-details h3 {
            margin-top: 0;
            color: #7c3aed;
        }
        
        .node-details p {
            color: #a0a0a0;
            line-height: 1.6;
        }
        
        .node-details .close {
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            color: #a0a0a0;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Obsidian-Style GBrain Graph</h1>
            <p>Wiki-style links and force-directed graph visualization</p>
        </div>
        
        <div class="stats">
            <span id="node-count">Nodes: 0</span>
            <span id="edge-count">Edges: 0</span>
            <span id="idea-count">Total Ideas: 0</span>
        </div>
        
        <div class="phase-legend">
            <div class="legend-item"><div class="legend-color" style="background: #4CAF50;"></div> Seed</div>
            <div class="legend-item"><div class="legend-color" style="background: #2196F3;"></div> Sprout</div>
            <div class="legend-item"><div class="legend-color" style="background: #FF9800;"></div> Growth</div>
            <div class="legend-item"><div class="legend-color" style="background: #9C27B0;"></div> Flower</div>
            <div class="legend-item"><div class="legend-color" style="background: #F44336;"></div> Harvest</div>
        </div>
        
        <div class="graph-container" id="graph"></div>
        
        <div class="controls">
            <button onclick="loadGraph()">🔄 Refresh Graph</button>
            <button onclick="zoomIn()">🔍+ Zoom In</button>
            <button onclick="zoomOut()">🔍- Zoom Out</button>
        </div>
    </div>
    
    <div id="node-details" class="node-details" style="display: none;">
        <button class="close" onclick="closeDetails()">×</button>
        <h3 id="detail-title">Node Details</h3>
        <div id="detail-content"></div>
    </div>
    
    <script>
        let currentZoom = 1;
        let simulation;
        let svg, g;
        
        const phaseColors = {
            seed: '#4CAF50',
            sprout: '#2196F3',
            growth: '#FF9800',
            flower: '#9C27B0',
            harvest: '#F44336'
        };
        
        async function loadGraph() {
            try {
                const response = await fetch('/api/graph/files');
                const data = await response.json();
                
                if (data.status === 'success') {
                    document.getElementById('node-count').textContent = \`Nodes: \${data.graph.nodes.length}\`;
                    document.getElementById('edge-count').textContent = \`Edges: \${data.graph.edges.length}\`;
                    document.getElementById('idea-count').textContent = \`Total Ideas: \${data.metadata.total_ideas}\`;
                    
                    renderGraph(data.graph.nodes, data.graph.edges);
                }
            } catch (error) {
                console.error('Error loading graph:', error);
                alert('Failed to load graph: ' + error.message);
            }
        }
        
        function renderGraph(nodes, edges) {
            const container = document.getElementById('graph');
            container.innerHTML = '';
            
            const width = container.clientWidth;
            const height = 500;
            
            svg = d3.select('#graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            g = svg.append('g');
            
            // Zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on('zoom', (event) => {
                    g.attr('transform', event.transform);
                    currentZoom = event.transform.k;
                });
            
            svg.call(zoom);
            
            // Force simulation
            simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(30));
            
            // Draw edges
            const link = g.append('g')
                .selectAll('line')
                .data(edges)
                .join('line')
                .attr('class', 'link')
                .attr('stroke-width', 2);
            
            // Draw nodes
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
            
            // Add labels
            const labels = g.append('g')
                .selectAll('text')
                .data(nodes)
                .join('text')
                .attr('class', 'node-label')
                .text(d => d.label)
                .attr('text-anchor', 'middle')
                .attr('dy', 35);
            
            // Update positions on simulation tick
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                labels
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            });
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
        
        function showNodeDetails(d) {
            const details = document.getElementById('node-details');
            document.getElementById('detail-title').textContent = d.label;
            document.getElementById('detail-content').innerHTML = \`
                <p><strong>Phase:</strong> \${d.phase}</p>
                <p><strong>ID:</strong> \${d.id}</p>
                <p><strong>Content Preview:</strong></p>
                <p>\${d.content || 'No content'}</p>
            \`;
            details.style.display = 'block';
        }
        
        function closeDetails() {
            document.getElementById('node-details').style.display = 'none';
        }
        
        function zoomIn() {
            svg.transition().duration(300).call(
                d3.zoom().scaleBy(1.3)
            );
        }
        
        function zoomOut() {
            svg.transition().duration(300).call(
                d3.zoom().scaleBy(0.7)
            );
        }
        
        // Load graph on page load
        loadGraph();
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

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🧠 Obsidian-Style Graph Server running on http://localhost:${PORT}`);
  console.log(`📁 Reading GBrain files from: ${GBBRAIN_SOURCE}`);
  console.log(`🌐 Open http://localhost:${PORT} for the graph viewer`);
});