#!/bin/bash
# Wiki-Reader - Manually processes wiki documents for agent consumption

WIKI_DIR="$HOME/.wuphf/wiki"
OUTPUT_DIR="$HOME/.wuphf/wiki/compiled"
AGENTS_DIR="$HOME/.wuphf/wiki/agents"

echo "📚 WIKI-READER - Processing wiki documents for agents"
echo "Wiki directory: $WIKI_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process key wiki documents
echo "📄 Processing key wiki documents..."

# 1. System Constraints
if [ -f "$WIKI_DIR/TEAM-CONSTRAINTS.md" ]; then
    cp "$WIKI_DIR/TEAM-CONSTRAINTS.md" "$OUTPUT_DIR/"
    echo "✅ TEAM-CONSTRAINTS.md"
fi

# 2. Output Guidelines
if [ -f "$WIKI_DIR/output-guidelines.md" ]; then
    cp "$WIKI_DIR/output-guidelines.md" "$OUTPUT_DIR/"
    echo "✅ output-guidelines.md"
fi

# 3. Research Limitations
if [ -f "$WIKI_DIR/research-limitations.md" ]; then
    cp "$WIKI_DIR/research-limitations.md" "$OUTPUT_DIR/"
    echo "✅ research-limitations.md"
fi

# 4. Team Knowledge
echo ""
echo "📚 Processing team knowledge..."
if [ -d "$WIKI_DIR/team" ]; then
    cp -r "$WIKI_DIR/team" "$OUTPUT_DIR/"
    echo "✅ team/ directory copied"
fi

# 5. Agent-specific information
echo ""
echo "🤖 Processing agent-specific information..."
if [ -d "$WIKI_DIR/agents" ]; then
    cp -r "$WIKI_DIR/agents" "$OUTPUT_DIR/"
    echo "✅ agents/ directory copied"
fi

# 6. Create index file
echo ""
echo "📋 Creating wiki index..."
cat > "$OUTPUT_DIR/WIKI-INDEX.md" << 'EOF'
# Wiki Index - Agent Knowledge Base

**Last updated**: $(date)
**Purpose**: Central index of all available knowledge for agents

---

## CRITICAL READING (Read First)

### System Constraints
- **File**: `TEAM-CONSTRAINTS.md`
- **Purpose**: Tool restrictions and allowed approaches
- **Priority**: MUST READ before any work

### Output Guidelines  
- **File**: `output-guidelines.md`
- **Purpose**: Where and how to store deliverables
- **Priority**: MUST READ for task completion

### Research Limitations
- **File**: `research-limitations.md`
- **Purpose**: How to conduct research without web search
- **Priority**: MUST READ for research tasks

---

## TEAM KNOWLEDGE

### Strategy & Positioning
- `team/agency-strategy.md` - Business strategy and goals
- `team/about/company.md` - Company profile and mission
- `team/quick-start-guide.md` - Quick reference for agents

### Skills & Methodologies
- `team/skills/` - Agent-specific skills and workflows
- `team/methodology/` - Agency methodologies and frameworks
- `team/playbooks/` - Standard operating procedures

### Research & Insights
- `team/research/` - Market research and analysis
- `team/case-studies/` - Case studies and examples

---

## AGENT-SPECIFIC INFORMATION

### CEO Agent
- `agents/ceo/` - CEO-specific knowledge and prompts
- Focus: Strategy, client management, team coordination

### SDR Agent
- `agents/sdr/` - SDR-specific knowledge (if exists)
- Focus: Lead generation, outreach, communication

### Research Agent
- `agents/research/` - Research-specific knowledge (if exists)
- Focus: Analysis, market research, data synthesis

### Content Agent
- `agents/content/` - Content-specific knowledge (if exists)
- Focus: Creation, storytelling, design

---

## TASK ASSIGNMENTS

### Current Tasks
- `../tasks/` - All available tasks
- Priority: Read 00-AGENT-STARTUP-READ-CONSTRAINTS.md first

### Task Types
- **CEO Tasks**: Strategic planning, client management
- **SDR Tasks**: Outreach, lead generation, communication
- **Research Tasks**: Analysis, market research, insights
- **Content Tasks**: Creation, decks, copywriting

---

## SUCCESS CRITERIA

### For All Agents
1. Read TEAM-CONSTRAINTS.md before any work
2. Store outputs in `~/wuphf-agency-output/`
3. Use internal knowledge only (no web search)
4. Document limitations clearly
5. Deliver professional quality

### For Task Completion
1. Output file created in correct location
2. File follows naming conventions
3. Content is useful and actionable
4. Limitations are documented
5. Victory Log updated

---

**Remember**: All knowledge you need is in this wiki. You don't need external search.

**Last updated**: $(date)
EOF

echo "✅ WIKI-INDEX.md created"

# 7. Create agent startup files
echo ""
echo "🚀 Creating agent startup files..."

for agent in ceo sdr research content; do
    if [ -d "$WIKI_DIR/agents/$agent" ] || [ "$agent" = "ceo" ]; then
        cat > "$OUTPUT_DIR/$agent-STARTUP.md" << EOF
# $agent Agent - Startup Instructions

**Agent**: $agent
**Startup Date**: $(date)
**Status**: Ready for task assignment

---

## IMMEDIATE ACTIONS

1. **Read Critical Documents** (5 minutes):
   - TEAM-CONSTRAINTS.md
   - output-guidelines.md
   - research-limitations.md

2. **Understand Your Role** (5 minutes):
   - Review agent-specific knowledge in agents/$agent/
   - Understand your responsibilities and tools

3. **Check Available Tasks** (2 minutes):
   - Review tasks/ directory
   - Identify tasks assigned to $agent agent

4. **Accept First Task**:
   - Choose appropriate task
   - Confirm you've read constraints
   - Begin work following guidelines

---

## YOUR CAPABILITIES

### Tools You HAVE Access To
- Wiki knowledge base (all documents in this directory)
- File operations (read/write outputs)
- Logical reasoning and analysis
- Strategic frameworks (Sequoia, YC, a16z)
- Content creation and documentation

### Tools You DO NOT Have Access To
- Google Search (any variant)
- Web scraping or browsing
- External APIs or data services
- Real-time web data fetching

---

## SUCCESS METRICS

### Task Completion
- Outputs stored in correct directories
- Files follow naming conventions
- Content is actionable and valuable
- Limitations clearly documented

### Quality Standards
- Professional language and formatting
- Strategic thinking applied
- Frameworks utilized appropriately
- Client-ready deliverables

---

## GETTING HELP

### If You're Stuck
1. Check relevant wiki documents
2. Apply logical frameworks
3. Document what information you need
4. Request specific data from client

### If You Encounter Tool Errors
1. Remember: External tools are not available
2. Use alternative approaches
3. Focus on what you CAN do with available resources
4. Deliver value despite limitations

---

**You are ready to begin. Read the constraints, accept a task, and deliver value!**

*Startup completed: $(date)*
EOF
        echo "✅ $agent-STARTUP.md created"
    fi
done

echo ""
echo "🎉 Wiki-Reader completed!"
echo "Compiled wiki available at: $OUTPUT_DIR"
echo "Total files processed: $(find $OUTPUT_DIR -type f | wc -l)"
echo ""
echo "Agents should now be able to access all wiki knowledge from: $OUTPUT_DIR"