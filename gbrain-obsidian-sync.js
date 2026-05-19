#!/usr/bin/env node

/**
 * GBrain → Obsidian Converter
 * 
 * Konvertiert GBrain Markdown-Dateien in Obsidian-Format
 * und erstellt einen Obsidian-Vault mit Graph-Support
 */

const fs = require('fs');
const path = require('path');

const GBBRAIN_SOURCE = path.join(process.env.HOME, 'ideen-growth-system');
const OBSIDIAN_VAULT = '/home/dyai/obsidian-vault';

// ── Konfiguration ─────────────────────────────────────────────

const OBSIDIAN_CONFIG = {
  'app.json': {
    'theme': 'obsidian',
    'baseFontSize': 16,
    'cssTheme': 'moonstone',
    'enabledCssSnippets': [],
    'communityPlugins': [],
    'plugins': [
      'graph',
      'kanban'
    ]
  },
  'graph.json': {
    'local': true,
    'folders': [],
    'files': [],
    'links': [],
    'attachmentFolderPath': 'attachments'
  },
  'kanban.json': {
    'kanban-plugin': {
      'date-format': 'YYYY-MM-DD',
      'date-display-format': 'YYYY-MM-DD',
      'time-format': 'HH:mm',
      'date-picker-week-start': 1,
      'date-picker-week-format': 'YYYY-[W]ww'
    }
  }
};

// ── Konvertierungsfunktionen ───────────────────────────────────

function convertGBrainToObsidian(gbrainFile, obsidianPath) {
  const content = fs.readFileSync(gbrainFile, 'utf-8');
  
  // Parse frontmatter
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
  
  // Extrahiere Phase aus Dateipfad
  const phase = gbrainFile.split('/').slice(-2, -1)[0].replace(/s$/, ''); // seeds -> seed
  
  // Konvertiere zu Obsidian-Format
  const obsidianContent = `---
tags: [idea, ${phase}]
phase: ${phase}
created: ${metadata.date || new Date().toISOString().split('T')[0]}
title: ${metadata.title || path.basename(gbrainFile, '.md')}
---

# ${metadata.title || path.basename(gbrainFile, '.md')}

${bodyContent}

---
## Metadata
- **Type**: ${metadata.type || 'concept'}
- **Phase**: ${phase}
- **Source**: GBrain
- **Original File**: \`${gbrainFile}\`
`;

  return obsidianContent;
}

function syncGBrainToObsidian() {
  console.log('🔄 Starting GBrain → Obsidian sync...');
  
  const phases = ['seeds', 'sprouts', 'growth', 'flowers', 'harvest'];
  let totalConverted = 0;
  
  // Stelle sicher dass Obsidian-Verzeichnis existiert
  if (!fs.existsSync(OBSIDIAN_VAULT)) {
    fs.mkdirSync(OBSIDIAN_VAULT, { recursive: true });
  }
  
  // Erstelle Obsidian-Konfiguration
  Object.entries(OBSIDIAN_CONFIG).forEach(([filename, config]) => {
    const configPath = path.join(OBSIDIAN_VAULT, '.obsidian', filename);
    if (!fs.existsSync(path.join(OBSIDIAN_VAULT, '.obsidian'))) {
      fs.mkdirSync(path.join(OBSIDIAN_VAULT, '.obsidian'), { recursive: true });
    }
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  });
  
  // Konvertiere jede Phase
  phases.forEach(phase => {
    const phaseDir = path.join(GBBRAIN_SOURCE, phase);
    const obsidianPhaseDir = path.join(OBSIDIAN_VAULT, phase);
    
    if (fs.existsSync(phaseDir)) {
      // Erstelle Phase-Verzeichnis im Obsidian-Vault
      if (!fs.existsSync(obsidianPhaseDir)) {
        fs.mkdirSync(obsidianPhaseDir, { recursive: true });
      }
      
      const files = fs.readdirSync(phaseDir);
      
      files.forEach(file => {
        if (file.endsWith('.md') && !file.startsWith('.')) {
          const gbrainFile = path.join(phaseDir, file);
          const obsidianFile = path.join(obsidianPhaseDir, file);
          
          try {
            const obsidianContent = convertGBrainToObsidian(gbrainFile, obsidianFile);
            fs.writeFileSync(obsidianFile, obsidianContent);
            console.log(`✅ Converted: ${file} (${phase})`);
            totalConverted++;
          } catch (error) {
            console.error(`❌ Error converting ${file}:`, error.message);
          }
        }
      });
    }
  });
  
  // Erstelle Index-Datei für Obsidian
  const indexContent = `# 🧠 GBrain Obsidian Vault

Dieses Vault enthält alle GBrain-Ideen in Obsidian-Format mit Graph-Visualisierung.

## 📁 Struktur

${phases.map(phase => {
  const phaseDir = path.join(OBSIDIAN_VAULT, phase);
  const count = fs.existsSync(phaseDir) ? fs.readdirSync(phaseDir).filter(f => f.endsWith('.md')).length : 0;
  return `- **${phase.charAt(0).toUpperCase() + phase.slice(1)}**: ${count} Ideen`;
}).join('\n')}

## 🔗 Verknüpfungen

Verwende Wiki-style Links \`[[Ideen-Name]]\` um Ideen zu verknüpfen.

## 📊 Graph

Öffne den Graph in Obsidian: \`Strg + G\` oder klicke auf das Graph-Symbol in der linken Leiste.

## 📋 Kanban

Das Kanban-Plugin ist installiert für Task-Management.
`;

  fs.writeFileSync(path.join(OBSIDIAN_VAULT, 'README.md'), indexContent);
  
  console.log(`✅ Sync complete: ${totalConverted} files converted`);
  console.log(`📁 Obsidian Vault: ${OBSIDIAN_VAULT}`);
  console.log(`🌐 Öffne Obsidian mit diesem Vault als Graph`);
}

// ── Watcher für automatische Synchronisation ─────────────

function setupWatcher() {
  try {
    const chokidar = require('chokidar');
    
    console.log('👀 Setting up file watcher...');
    
    // Watch GBrain-Verzeichnis
    const watcher = chokidar.watch(GBBRAIN_SOURCE, {
      ignored: /(^|[\\/\\])\./,
      persistent: true
    });
    
    watcher.on('add', (filePath) => {
      if (filePath.endsWith('.md')) {
        console.log(`📄 New file detected: ${filePath}`);
        syncGBrainToObsidian();
      }
    });
    
    watcher.on('change', (filePath) => {
      if (filePath.endsWith('.md')) {
        console.log(`📝 File changed: ${filePath}`);
        syncGBrainToObsidian();
      }
    });
    
    console.log('👀 File watcher active. Changes in GBrain will auto-sync to Obsidian.');
  } catch (error) {
    console.log('⚠️  Chokidar not available. Install with: npm install chokidar');
    console.log('Running in manual sync mode only.');
  }
}

// ── Main ───────────────────────────────────────────────────

if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--watch')) {
    syncGBrainToObsidian();
    setupWatcher();
  } else {
    syncGBrainToObsidian();
  }
}

module.exports = { syncGBrainToObsidian, setupWatcher };