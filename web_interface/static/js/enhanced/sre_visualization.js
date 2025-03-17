/**
 * SRE Visualization JavaScript
 * 
 * This script provides interactive visualization of the Symbiotic Reflective Ecosystem (SRE)
 * with dynamic node connections and real-time metrics display.
 */

class SREVisualizer {
    constructor(options = {}) {
        // Set default options
        this.options = Object.assign({
            containerId: 'sreVisualization',
            canvasId: 'nodeCanvas',
            paradigmSelectorId: 'paradigmSelector',
            collapseButtonId: 'collapseBtn',
            metricsIds: {
                truthValue: 'truthValue',
                scrutinyValue: 'scrutinyValue',
                improvementValue: 'improvementValue',
                advancementValue: 'advancementValue',
                globalCoherence: 'globalCoherence',
                nodeCount: 'nodeCount'
            }
        }, options);
        
        // Initialize variables
        this.paradigm = 'conceptual_chaining';
        this.metaMetaStage = 'stageWhy';
        this.reasoningPaths = [];
        this.metrics = {
            truth: 0.7,
            scrutiny: 0.4,
            improvement: 0.6,
            advancement: 0.68,
            globalCoherence: 0.82,
            nodeCount: 4
        };
        
        this.nodes = [];
        this.connections = [];
        this.animationFrameId = null;
        
        // Initialize when document is ready
        document.addEventListener('DOMContentLoaded', () => this.initialize());
    }
    
    initialize() {
        // Get canvas element
        const canvas = document.getElementById(this.options.canvasId);
        if (canvas) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            
            // Initialize nodes and connections
            this.initializeNodes();
            
            // Start animation
            this.animate();
        }
        
        // Initialize event handlers
        this.initializeEventHandlers();
        
        // Update visualizations with initial data
        this.updateVisualization();
    }
    
    initializeEventHandlers() {
        // Paradigm selector
        const paradigmSelector = document.getElementById(this.options.paradigmSelectorId);
        if (paradigmSelector) {
            paradigmSelector.addEventListener('change', (e) => {
                this.paradigm = e.target.value;
                this.updateVisualization();
            });
        }
        
        // Meta-Meta stages
        const stages = document.querySelectorAll('.stage');
        stages.forEach(stage => {
            stage.addEventListener('click', (e) => {
                this.metaMetaStage = e.target.id;
                this.updateMetaMetaStages();
            });
        });
        
        // Collapse button
        const collapseBtn = document.getElementById(this.options.collapseButtonId);
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => {
                const content = document.querySelector('.sre-content');
                if (content) {
                    content.classList.toggle('collapsed');
                    
                    // Update button icon
                    const icon = collapseBtn.querySelector('i');
                    if (icon.classList.contains('bi-chevron-down')) {
                        icon.classList.replace('bi-chevron-down', 'bi-chevron-up');
                    } else {
                        icon.classList.replace('bi-chevron-up', 'bi-chevron-down');
                    }
                }
            });
        }
    }
    
    initializeNodes() {
        // Sample nodes representing different reasoning paradigms
        this.nodes = [
            {
                id: 'conceptual_chaining',
                x: this.canvas.width * 0.3,
                y: this.canvas.height * 0.3,
                radius: 25,
                color: '#4285f4',
                resonance: 0.8,
                pulsing: true
            },
            {
                id: 'chunked_symbolism',
                x: this.canvas.width * 0.7,
                y: this.canvas.height * 0.3,
                radius: 20,
                color: '#ea4335',
                resonance: 0.6,
                pulsing: true
            },
            {
                id: 'expert_lexicons',
                x: this.canvas.width * 0.3,
                y: this.canvas.height * 0.7,
                radius: 18,
                color: '#fbbc05',
                resonance: 0.5,
                pulsing: true
            },
            {
                id: 'socratic_questioning',
                x: this.canvas.width * 0.7,
                y: this.canvas.height * 0.7,
                radius: 22,
                color: '#34a853',
                resonance: 0.7,
                pulsing: true
            }
        ];
        
        // Create connections between all nodes
        this.connections = [];
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                this.connections.push({
                    from: this.nodes[i],
                    to: this.nodes[j],
                    strength: Math.random() * 0.5 + 0.25,  // 0.25-0.75
                    pulsing: true
                });
            }
        }
    }
    
    updateMetaMetaStages() {
        const stages = document.querySelectorAll('.stage');
        stages.forEach(stage => {
            if (stage.id === this.metaMetaStage) {
                stage.classList.add('active');
            } else {
                stage.classList.remove('active');
            }
        });
    }
    
    updateReasoningPaths(paths) {
        this.reasoningPaths = paths;
        const container = document.getElementById('reasoningPaths');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (paths.length === 0) {
            container.innerHTML = '<div class="text-muted">No reasoning paths available</div>';
            return;
        }
        
        paths.forEach(path => {
            const pathEl = document.createElement('div');
            pathEl.className = 'reasoning-path';
            
            pathEl.innerHTML = `
                <div class="path-header">${path.name}</div>
                <div class="path-steps">
                    ${path.steps.map(step => `<div class="path-step">${step}</div>`).join('')}
                </div>
            `;
            
            container.appendChild(pathEl);
        });
    }
    
    updateMetrics(metrics = null) {
        // Use provided metrics or current metrics
        const m = metrics || this.metrics;
        
        // Update metrics display
        const ids = this.options.metricsIds;
        
        if (document.getElementById(ids.truthValue)) {
            document.getElementById(ids.truthValue).textContent = m.truth.toFixed(2);
            document.querySelector(`#${ids.truthValue} + .metric-bar .metric-fill`).style.width = `${m.truth * 100}%`;
        }
        
        if (document.getElementById(ids.scrutinyValue)) {
            document.getElementById(ids.scrutinyValue).textContent = m.scrutiny.toFixed(2);
            document.querySelector(`#${ids.scrutinyValue} + .metric-bar .metric-fill`).style.width = `${m.scrutiny * 100}%`;
        }
        
        if (document.getElementById(ids.improvementValue)) {
            document.getElementById(ids.improvementValue).textContent = m.improvement.toFixed(2);
            document.querySelector(`#${ids.improvementValue} + .metric-bar .metric-fill`).style.width = `${m.improvement * 100}%`;
        }
        
        if (document.getElementById(ids.advancementValue)) {
            document.getElementById(ids.advancementValue).textContent = m.advancement.toFixed(2);
            document.querySelector(`#${ids.advancementValue} + .metric-bar .metric-fill`).style.width = `${m.advancement * 100}%`;
        }
        
        if (document.getElementById(ids.globalCoherence)) {
            document.getElementById(ids.globalCoherence).textContent = m.globalCoherence.toFixed(2);
        }
        
        if (document.getElementById(ids.nodeCount)) {
            document.getElementById(ids.nodeCount).textContent = m.nodeCount;
        }
    }
    
    updateVisualization(data = null) {
        // If data is provided, update everything
        if (data) {
            // Update metrics
            if (data.metrics) {
                this.metrics = {
                    truth: data.metrics.truth_value || 0.7,
                    scrutiny: data.metrics.scrutiny_value || 0.3,
                    improvement: data.metrics.improvement_value || 0.5,
                    advancement: data.metrics.advancement || 0.6,
                    globalCoherence: data.metrics.global_coherence || 0.8,
                    nodeCount: data.nodes?.length || 4
                };
            }
            
            // Update nodes if provided
            if (data.nodes) {
                // TODO: Update this when real node data is available
                this.nodes.forEach(node => {
                    const matchingNode = data.nodes.find(n => n.paradigm === node.id);
                    if (matchingNode) {
                        node.resonance = matchingNode.weight || 0.5;
                    }
                });
            }
            
            // Update reasoning paths
            if (data.reasoning_paths) {
                this.updateReasoningPaths(data.reasoning_paths);
            }
            
            // Update meta-meta stage
            if (data.meta_meta_stage) {
                this.metaMetaStage = data.meta_meta_stage;
                this.updateMetaMetaStages();
            }
            
            // Update paradigm
            if (data.paradigm) {
                this.paradigm = data.paradigm;
                const selector = document.getElementById(this.options.paradigmSelectorId);
                if (selector) {
                    selector.value = data.paradigm;
                }
            }
        } else {
            // Generate sample data for demonstration
            const newMetrics = {
                truth: Math.random() * 0.4 + 0.6,  // 0.6 - 1.0
                scrutiny: Math.random() * 0.6 + 0.2,  // 0.2 - 0.8
                improvement: Math.random() * 0.6 + 0.3,  // 0.3 - 0.9
                advancement: 0,
                globalCoherence: this.metrics.globalCoherence,
                nodeCount: this.nodes.length
            };
            
            // Calculate advancement
            newMetrics.advancement = newMetrics.truth * 0.4 + 
                                    newMetrics.scrutiny * 0.3 + 
                                    newMetrics.improvement * 0.3;
                                    
            this.metrics = newMetrics;
            
            // Generate sample reasoning paths based on paradigm
            let samplePaths = [];
            
            if (this.paradigm === 'conceptual_chaining') {
                samplePaths = [
                    {
                        name: 'Concept Chain: Decision Making',
                        steps: ['Identify Choice', 'Consider Options', 'Evaluate Consequences', 'Determine Value Alignment', 'Make Decision']
                    }
                ];
            } else if (this.paradigm === 'chunked_symbolism') {
                samplePaths = [
                    {
                        name: 'Symbolic Analysis: Efficiency',
                        steps: ['Define Variables', 'Establish Metrics', 'Express Relationships', 'Analyze Boundary Conditions', 'Formulate Equation']
                    }
                ];
            } else if (this.paradigm === 'expert_lexicons') {
                samplePaths = [
                    {
                        name: 'Domain Analysis: Process Optimization',
                        steps: ['Context Definition', 'Technical Specification', 'Standard Application', 'Domain Implementation', 'Expert Verification']
                    }
                ];
            } else {
                samplePaths = [
                    {
                        name: 'Socratic Inquiry: Understanding',
                        steps: ['What is meant?', 'What evidence exists?', 'What alternatives exist?', 'What assumptions underlie?', 'What implications follow?']
                    }
                ];
            }
            
            this.updateReasoningPaths(samplePaths);
        }
        
        // Update metrics display
        this.updateMetrics();
    }
    
    drawNode(node, time) {
        if (!this.ctx) return;
        
        const ctx = this.ctx;
        
        // Calculate pulse effect
        const pulse = node.pulsing ? Math.sin(time * 0.003) * 0.1 + 0.9 : 1;
        const radius = node.radius * pulse * node.resonance;
        
        // Draw main node circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.globalAlpha = 0.7 * node.resonance;
        ctx.fill();
        
        // Draw outer glow
        const gradient = ctx.createRadialGradient(
            node.x, node.y, radius * 0.8,
            node.x, node.y, radius * 1.5
        );
        gradient.addColorStop(0, node.color + '40');  // 25% opacity
        gradient.addColorStop(1, node.color + '00');  // 0% opacity
        
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.globalAlpha = 0.5 * node.resonance;
        ctx.fill();
        
        // Reset alpha
        ctx.globalAlpha = 1.0;
    }
    
    drawConnection(conn, time) {
        if (!this.ctx) return;
        
        const ctx = this.ctx;
        const from = conn.from;
        const to = conn.to;
        
        // Calculate pulse effect for line
        const pulse = conn.pulsing ? Math.sin(time * 0.002) * 0.2 + 0.8 : 1;
        const strength = conn.strength * pulse;
        
        // Draw connection line
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        
        // Use gradient based on node colors
        const gradient = ctx.createLinearGradient(from.x, from.y, to.x, to.y);
        gradient.addColorStop(0, from.color + '80');  // 50% opacity
        gradient.addColorStop(1, to.color + '80');    // 50% opacity
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2 * strength;
        ctx.globalAlpha = 0.6 * strength;
        ctx.stroke();
        
        // Reset alpha
        ctx.globalAlpha = 1.0;
        
        // Draw energy particles moving along the connection
        this.drawEnergyParticles(from, to, time, strength);
    }
    
    drawEnergyParticles(from, to, time, strength) {
        if (!this.ctx) return;
        
        const ctx = this.ctx;
        
        // Calculate direction vector
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        // Number of particles based on connection strength
        const particleCount = Math.floor(3 * strength);
        
        for (let i = 0; i < particleCount; i++) {
            // Calculate particle position along the line
            const offset = ((time * 0.05) + i * (100 / particleCount)) % 100;
            const t = offset / 100;
            
            const x = from.x + dx * t;
            const y = from.y + dy * t;
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(x, y, 2 * strength, 0, Math.PI * 2);
            
            // Gradient color based on position
            const color = t < 0.5 ? from.color : to.color;
            ctx.fillStyle = color;
            ctx.globalAlpha = 0.8 * strength;
            ctx.fill();
        }
        
        // Reset alpha
        ctx.globalAlpha = 1.0;
    }
    
    animate() {
        if (!this.ctx) return;
        
        const time = Date.now();
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw connections first (behind nodes)
        this.connections.forEach(conn => this.drawConnection(conn, time));
        
        // Draw nodes
        this.nodes.forEach(node => this.drawNode(node, time));
        
        // Continue animation
        this.animationFrameId = requestAnimationFrame(() => this.animate());
    }
    
    stop() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }
}

// Create a global instance
let sreVisualizer = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    sreVisualizer = new SREVisualizer();
    
    // Make visualizer globally available for API access
    window.sreVisualizer = sreVisualizer;
});
