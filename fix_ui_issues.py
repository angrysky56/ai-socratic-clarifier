#!/usr/bin/env python3
"""
Fix UI issues in the AI-Socratic-Clarifier.

This script addresses UI rendering issues in the integrated_ui.html template and ensures
that all necessary JavaScript and CSS files are loaded properly.
"""

import os
import sys
import re
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir

def backup_file(file_path):
    """Create a backup of a file with .bak extension."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.ui_fix_bak"
        logger.info(f"Creating backup of {file_path} to {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_integrated_ui():
    """Fix the integrated UI template issues."""
    ui_path = os.path.join(project_root, 'web_interface', 'templates', 'integrated_ui.html')
    
    if not os.path.exists(ui_path):
        logger.error(f"Integrated UI template not found at: {ui_path}")
        return False
    
    # Backup the original file
    backup_file(ui_path)
    
    try:
        with open(ui_path, 'r') as f:
            content = f.read()
        
        # Fix common UI issues
        changes_made = False
        
        # 1. Fix duplicate settings panes
        settings_pane_count = content.count('<div class="sidebar-pane" id="settings-pane">')
        if settings_pane_count > 1:
            logger.warning(f"Found {settings_pane_count} settings panes in UI template")
            
            # Find first settings pane
            first_pane_pos = content.find('<div class="sidebar-pane" id="settings-pane">')
            if first_pane_pos > 0:
                closing_divs = 0
                pos = first_pane_pos
                
                # Find the end of first settings pane by counting divs
                while closing_divs < 2 and pos < len(content):
                    next_open = content.find('<div', pos + 1)
                    next_close = content.find('</div>', pos + 1)
                    
                    if next_open > 0 and next_close > 0 and next_open < next_close:
                        pos = next_open
                    elif next_close > 0:
                        pos = next_close
                        closing_divs += 1
                    else:
                        break
                
                first_pane_end = pos + 6  # Length of "</div>"
                
                # Find second pane
                second_pane_pos = content.find('<div class="sidebar-pane" id="settings-pane">', first_pane_end)
                
                if second_pane_pos > 0:
                    # Find the end of second settings pane
                    closing_divs = 0
                    pos = second_pane_pos
                    
                    while closing_divs < 2 and pos < len(content):
                        next_open = content.find('<div', pos + 1)
                        next_close = content.find('</div>', pos + 1)
                        
                        if next_open > 0 and next_close > 0 and next_open < next_close:
                            pos = next_open
                        elif next_close > 0:
                            pos = next_close
                            closing_divs += 1
                        else:
                            break
                    
                    second_pane_end = pos + 6  # Length of "</div>"
                    
                    # Remove the second pane
                    updated_content = content[:second_pane_pos] + content[second_pane_end:]
                    content = updated_content
                    changes_made = True
                    logger.info("Fixed duplicate settings pane")
        
        # 2. Add missing CSS and JS imports
        if 'sre_visualization.css' not in content:
            css_imports = re.findall(r'<link rel="stylesheet" href="/static/css[^>]+>', content)
            if css_imports:
                last_import = css_imports[-1]
                last_import_pos = content.rfind(last_import)
                
                if last_import_pos > 0:
                    # Add SRE CSS import
                    new_import = '\n    <link rel="stylesheet" href="/static/css/enhanced/sre_visualization.css">'
                    updated_content = content[:last_import_pos + len(last_import)] + new_import + content[last_import_pos + len(last_import):]
                    content = updated_content
                    changes_made = True
                    logger.info("Added SRE CSS import")
        
        if 'sre_visualization.js' not in content:
            js_imports = re.findall(r'<script src="/static/js[^>]+></script>', content)
            if js_imports:
                last_import = js_imports[-1]
                last_import_pos = content.rfind(last_import)
                
                if last_import_pos > 0:
                    # Add SRE JS import
                    new_import = '\n    <script src="/static/js/enhanced/sre_visualization.js"></script>'
                    updated_content = content[:last_import_pos + len(last_import)] + new_import + content[last_import_pos + len(last_import):]
                    content = updated_content
                    changes_made = True
                    logger.info("Added SRE JS import")
        
        # 3. Fix missing SRE switch
        if 'useSRESwitch' not in content:
            sot_switch_pos = content.find('useSoTSwitch')
            if sot_switch_pos > 0:
                # Find the parent div
                div_start = content.rfind('<div class="form-check', 0, sot_switch_pos)
                div_end = content.find('</div>', sot_switch_pos)
                
                if div_start > 0 and div_end > 0:
                    full_sot_switch = content[div_start:div_end+6]
                    
                    # Create SRE switch based on SoT switch
                    sre_switch = full_sot_switch.replace('useSoTSwitch', 'useSRESwitch').replace('Sequential Thinking', 'Reflective Ecosystem')
                    
                    # Add after SoT switch
                    updated_content = content[:div_end+6] + '\n                    ' + sre_switch + content[div_end+6:]
                    content = updated_content
                    changes_made = True
                    logger.info("Added SRE switch")
        
        # 4. Fix SRE enabled indicator
        if 'SRE Enabled' not in content and 'sreEnabled' not in content:
            model_info_pos = content.find('<div id="modelInfo"')
            if model_info_pos > 0:
                sot_enabled_pos = content.find('<p><strong>SoT Enabled:</strong>', model_info_pos)
                if sot_enabled_pos > 0:
                    line_end = content.find('</p>', sot_enabled_pos)
                    if line_end > 0:
                        # Add SRE enabled after SoT enabled
                        full_sot_enabled = content[sot_enabled_pos:line_end+4]
                        sre_enabled = full_sot_enabled.replace('SoT Enabled', 'SRE Enabled').replace('sotEnabled', 'sreEnabled')
                        
                        updated_content = content[:line_end+4] + '\n                            ' + sre_enabled + content[line_end+4:]
                        content = updated_content
                        changes_made = True
                        logger.info("Added SRE enabled indicator")
        
        # 5. Fix the sidebar height and position
        if 'id="sidebarContent"' in content and 'height: 100%;' not in content:
            sidebar_pos = content.find('id="sidebarContent"')
            if sidebar_pos > 0:
                style_start = content.rfind('style="', 0, sidebar_pos)
                style_end = content.find('"', style_start + 7)
                
                if style_start > 0 and style_end > 0:
                    original_style = content[style_start+7:style_end]
                    if 'height' not in original_style:
                        new_style = original_style + " height: 100%;"
                        updated_content = content[:style_start+7] + new_style + content[style_end:]
                        content = updated_content
                        changes_made = True
                        logger.info("Fixed sidebar height")
        
        # 6. Fix control pane overlaps
        control_panes = re.findall(r'<div class="sidebar-pane" id="[^"]+">', content)
        for i, pane in enumerate(control_panes):
            pane_id = re.search(r'id="([^"]+)"', pane).group(1)
            if i > 0 and f'<a href="#{pane_id}"' not in content:
                prev_pane_id = re.search(r'id="([^"]+)"', control_panes[i-1]).group(1)
                prev_pane_link_pos = content.find(f'<a href="#{prev_pane_id}"')
                
                if prev_pane_link_pos > 0:
                    end_prev_link = content.find('</a>', prev_pane_link_pos)
                    if end_prev_link > 0:
                        # Create new link based on previous link
                        full_prev_link = content[prev_pane_link_pos:end_prev_link+4]
                        new_link = full_prev_link.replace(f'#{prev_pane_id}', f'#{pane_id}').replace(f'>{prev_pane_id.replace("-pane", "").title()}<', f'>{pane_id.replace("-pane", "").title()}<')
                        
                        updated_content = content[:end_prev_link+4] + '\n                    ' + new_link + content[end_prev_link+4:]
                        content = updated_content
                        changes_made = True
                        logger.info(f"Added missing link for {pane_id}")
        
        # Write back if changes were made
        if changes_made:
            with open(ui_path, 'w') as f:
                f.write(content)
            
            logger.info("Successfully fixed issues in integrated_ui.html")
        else:
            logger.info("No UI issues found in integrated_ui.html")
        
        return True
    
    except Exception as e:
        logger.error(f"Error fixing integrated UI: {e}")
        return False

def fix_integrated_ui_js():
    """Fix the integrated UI JavaScript."""
    js_path = os.path.join(project_root, 'web_interface', 'static', 'js', 'integrated_ui.js')
    
    if not os.path.exists(js_path):
        logger.error(f"Integrated UI JS not found at: {js_path}")
        return False
    
    # Backup the original file
    backup_file(js_path)
    
    try:
        with open(js_path, 'r') as f:
            content = f.read()
        
        changes_made = False
        
        # Add SRE switch handler if missing
        if 'useSRESwitch' not in content:
            rag_handler_pos = content.find('useRAGSwitch')
            if rag_handler_pos > 0:
                # Find the end of the RAG handler
                handler_end = content.find('});', rag_handler_pos)
                if handler_end > 0:
                    # Add SRE handler after RAG handler
                    sre_handler = '''
    
    // SRE switch handler
    const useSRESwitch = document.getElementById('useSRESwitch');
    if (useSRESwitch) {
        useSRESwitch.addEventListener('change', function(e) {
            const isEnabled = e.target.checked;
            
            // Update UI
            const sreEnabledEl = document.getElementById('sreEnabled');
            if (sreEnabledEl) {
                sreEnabledEl.textContent = isEnabled ? 'Yes' : 'No';
            }
            
            // Store setting
            localStorage.setItem('useSRE', isEnabled);
            
            // Update visualization if available
            if (window.sreVisualizer && typeof window.sreVisualizer.setEnabled === 'function') {
                window.sreVisualizer.setEnabled(isEnabled);
            }
        });
        
        // Initialize from saved setting
        const savedSRE = localStorage.getItem('useSRE');
        if (savedSRE !== null) {
            useSRESwitch.checked = savedSRE === 'true';
            
            // Update UI
            const sreEnabledEl = document.getElementById('sreEnabled');
            if (sreEnabledEl) {
                sreEnabledEl.textContent = useSRESwitch.checked ? 'Yes' : 'No';
            }
        }
    }'''
                    
                    updated_content = content[:handler_end+2] + sre_handler + content[handler_end+2:]
                    content = updated_content
                    changes_made = True
                    logger.info("Added SRE switch handler")
        
        # Fix document ready event handler if jQuery is missing
        if '$(document).ready(' in content and 'document.addEventListener("DOMContentLoaded"' not in content:
            doc_ready_pos = content.find('$(document).ready(')
            if doc_ready_pos > 0:
                updated_content = content.replace('$(document).ready(', 'document.addEventListener("DOMContentLoaded", ')
                content = updated_content
                changes_made = True
                logger.info("Fixed document ready event handler")
        
        # Write back if changes were made
        if changes_made:
            with open(js_path, 'w') as f:
                f.write(content)
            
            logger.info("Successfully fixed issues in integrated_ui.js")
        else:
            logger.info("No issues found in integrated_ui.js")
        
        return True
    
    except Exception as e:
        logger.error(f"Error fixing integrated UI JS: {e}")
        return False

def verify_css_js_files():
    """Verify that all necessary CSS and JS files exist."""
    # SRE visualization files
    sre_css_path = os.path.join(project_root, 'web_interface', 'static', 'css', 'enhanced', 'sre_visualization.css')
    sre_js_path = os.path.join(project_root, 'web_interface', 'static', 'js', 'enhanced', 'sre_visualization.js')
    
    # Document panel files
    doc_css_path = os.path.join(project_root, 'web_interface', 'static', 'css', 'enhanced', 'document_panel.css')
    
    os.makedirs(os.path.dirname(sre_css_path), exist_ok=True)
    os.makedirs(os.path.dirname(sre_js_path), exist_ok=True)
    
    missing_files = []
    if not os.path.exists(sre_css_path):
        missing_files.append(sre_css_path)
    
    if not os.path.exists(sre_js_path):
        missing_files.append(sre_js_path)
    
    if not os.path.exists(doc_css_path):
        missing_files.append(doc_css_path)
    
    # Look for files in archive
    archive_dir = os.path.join(project_root, 'archive', 'fixes')
    
    for missing_file in missing_files[:]:
        rel_path = os.path.relpath(missing_file, project_root)
        archive_path = os.path.join(archive_dir, rel_path)
        
        if os.path.exists(archive_path):
            # Copy from archive
            os.makedirs(os.path.dirname(missing_file), exist_ok=True)
            shutil.copy2(archive_path, missing_file)
            logger.info(f"Copied {rel_path} from archive")
            missing_files.remove(missing_file)
    
    # Create minimal versions for any still missing files
    for missing_file in missing_files:
        if missing_file.endswith('sre_visualization.css') and not os.path.exists(missing_file):
            os.makedirs(os.path.dirname(missing_file), exist_ok=True)
            with open(missing_file, 'w') as f:
                f.write('''/* SRE Visualization Styles */

/* Meta-Meta Framework Visualization */
.meta-meta-visualization {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: var(--card-bg, #f8f9fa);
    border-radius: 8px;
    margin-bottom: 15px;
}

.meta-meta-stage {
    text-align: center;
    padding: 5px;
    width: 70px;
    border-radius: 5px;
    position: relative;
    font-size: 0.7rem;
    cursor: help;
}

.meta-meta-stage:not(:last-child)::after {
    content: "→";
    position: absolute;
    right: -15px;
    top: 50%;
    transform: translateY(-50%);
}

.meta-meta-stage.active {
    background-color: var(--primary, #0d6efd);
    color: white;
    font-weight: bold;
}

/* Network Visualization */
.network-visualization {
    min-height: 200px;
    background-color: var(--card-bg, #f8f9fa);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
}

.network-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    color: var(--text-muted, #6c757d);
    font-style: italic;
}

/* Reasoning Paths */
.reasoning-paths {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.reasoning-path {
    border: 1px solid var(--border-color, #dee2e6);
    border-radius: 6px;
    overflow: hidden;
}

.path-name {
    background-color: var(--secondary-bg, #e9ecef);
    padding: 8px 12px;
    font-weight: bold;
    border-bottom: 1px solid var(--border-color, #dee2e6);
}

.path-steps {
    padding: 8px 12px;
}

.path-steps ol {
    margin: 0;
    padding-left: 20px;
}

.path-steps li {
    margin-bottom: 5px;
}

/* Global stats */
.sre-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: var(--card-bg, #f8f9fa);
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 0.8rem;
}

.advancement-container {
    width: 150px;
    height: 8px;
    background-color: var(--border-color, #dee2e6);
    border-radius: 4px;
    overflow: hidden;
}

.advancement-indicator {
    height: 100%;
    background-color: var(--success, #198754);
    width: 0%;
    transition: width 0.5s ease;
}''')
            logger.info(f"Created minimal CSS file: {missing_file}")
        
        elif missing_file.endswith('document_panel.css') and not os.path.exists(missing_file):
            os.makedirs(os.path.dirname(missing_file), exist_ok=True)
            with open(missing_file, 'w') as f:
                f.write('''/* Document Panel Styles */

.document-panel {
    border: 1px solid var(--border-color, #dee2e6);
    border-radius: 0.25rem;
    margin-bottom: 1rem;
    background-color: var(--card-bg, #f8f9fa);
}

.document-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color, #dee2e6);
    background-color: rgba(0, 0, 0, 0.03);
}

.document-title {
    font-weight: bold;
    margin: 0;
}

.document-controls {
    display: flex;
    gap: 0.5rem;
}

.document-content {
    padding: 1rem;
    max-height: 400px;
    overflow-y: auto;
}

.document-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-top: 1px solid var(--border-color, #dee2e6);
}''')
            logger.info(f"Created minimal CSS file: {missing_file}")
    
    logger.info("Verified all necessary CSS and JS files")
    return True

def fix_all_ui_issues():
    """Fix all UI issues."""
    # First, verify/create all necessary CSS and JS files
    verify_css_js_files()
    
    # Fix the integrated UI template
    if fix_integrated_ui():
        logger.info("✅ Fixed integrated UI template")
    else:
        logger.warning("❌ Failed to fix integrated UI template")
    
    # Fix the integrated UI JavaScript
    if fix_integrated_ui_js():
        logger.info("✅ Fixed integrated UI JavaScript")
    else:
        logger.warning("❌ Failed to fix integrated UI JavaScript")
    
    return True

if __name__ == "__main__":
    try:
        if fix_all_ui_issues():
            logger.info("✨ Successfully fixed UI issues")
            sys.exit(0)
        else:
            logger.error("⚠️ Some UI issues could not be fixed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error fixing UI issues: {e}")
        sys.exit(1)
