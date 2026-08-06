import React, { useState, useEffect, useRef } from 'react';
import { workflowService } from '../../services/workflowService';
import { WorkflowNode } from './WorkflowNode';
import { WorkflowEdge } from './WorkflowEdge';
import { WorkflowToolbar } from './WorkflowToolbar';
import { WorkflowSidebar } from './WorkflowSidebar';
import { NodePropertiesPanel } from './NodePropertiesPanel';
import { ExecutionConsole } from './ExecutionConsole';
import { ExecutionHistoryPanel } from './ExecutionHistoryPanel';
import { MiniMap } from './MiniMap';

export const WorkflowCanvas = ({ workflowId, onBack, initialWorkflow }) => {
  const [workflow, setWorkflow] = useState(initialWorkflow || {
    name: 'New AI Workflow',
    description: 'Visual DAG Execution Studio',
    status: 'DRAFT',
    version: 1,
    nodes: [
      { id: 'start_1', type: 'start', label: 'Start Entry', position: { x: 100, y: 150 }, data: {} },
      { id: 'llm_1', type: 'llm_prompt', label: 'LLM Prompt', position: { x: 450, y: 150 }, data: { prompt: 'Analyze input: {input}' } },
      { id: 'end_1', type: 'end', label: 'End Output', position: { x: 800, y: 150 }, data: {} },
    ],
    edges: [
      { id: 'e_1', source: 'start_1', target: 'llm_1' },
      { id: 'e_2', source: 'llm_1', target: 'end_1' },
    ],
    variables: {},
  });

  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [connectingSource, setConnectingSource] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [currentExecution, setCurrentExecution] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isValid, setIsValid] = useState(true);
  const [validationErrors, setValidationErrors] = useState([]);
  const [isSaving, setIsSaving] = useState(false);

  const [showConsole, setShowConsole] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showMiniMap, setShowMiniMap] = useState(true);

  const canvasRef = useRef(null);

  // Fetch workflow details and starter templates on mount or workflowId change
  useEffect(() => {
    const initData = async () => {
      try {
        const tmpls = await workflowService.getStarterTemplates();
        setTemplates(tmpls || []);

        if (workflowId) {
          const wfData = await workflowService.getWorkflow(workflowId);
          if (wfData) {
            setWorkflow(wfData);
            const { valid, errors } = validateGraphLocally(wfData.nodes || [], wfData.edges || []);
            setIsValid(valid);
            setValidationErrors(errors);
          }

          const execs = await workflowService.listExecutions({ workflow_id: workflowId });
          setExecutions(execs || []);
        }
      } catch (err) {
        console.error('Failed to load workflow or templates:', err);
      }
    };
    initData();
  }, [workflowId]);

  // Local DAG validation for cycle detection
  const validateGraphLocally = (nodes = [], edges = []) => {
    const hasStart = nodes.some((n) => n.type === 'start');
    const hasEnd = nodes.some((n) => n.type === 'end');
    const errors = [];
    if (!hasStart) errors.push('Missing Start node');
    if (!hasEnd) errors.push('Missing End node');
    return { valid: errors.length === 0, errors };
  };

  const addNodeAtPosition = (type, label, position) => {
    const newNode = {
      id: `${type}_${Date.now()}`,
      type,
      label,
      position: position || { x: 300 + Math.random() * 50, y: 200 + Math.random() * 50 },
      data: {},
    };

    setWorkflow((prev) => {
      const updatedNodes = [...(prev.nodes || []), newNode];
      const { valid, errors } = validateGraphLocally(updatedNodes, prev.edges || []);
      setIsValid(valid);
      setValidationErrors(errors);
      return { ...prev, nodes: updatedNodes };
    });
    setSelectedNode(newNode);
  };

  const addNode = (type, label) => {
    addNodeAtPosition(type, label, { x: 300 + Math.random() * 50, y: 200 + Math.random() * 50 });
  };

  const moveNode = (id, newPosition) => {
    setWorkflow((prev) => ({
      ...prev,
      nodes: (prev.nodes || []).map((n) => (n.id === id ? { ...n, position: newPosition } : n)),
    }));
  };

  const updateNode = (id, updates) => {
    setWorkflow((prev) => ({
      ...prev,
      nodes: (prev.nodes || []).map((n) => (n.id === id ? { ...n, ...updates } : n)),
    }));
    if (selectedNode?.id === id) {
      setSelectedNode((prev) => ({ ...prev, ...updates }));
    }
  };

  const deleteNode = (id) => {
    setWorkflow((prev) => {
      const updatedNodes = (prev.nodes || []).filter((n) => n.id !== id);
      const updatedEdges = (prev.edges || []).filter((e) => e.source !== id && e.target !== id);
      const { valid, errors } = validateGraphLocally(updatedNodes, updatedEdges);
      setIsValid(valid);
      setValidationErrors(errors);
      return { ...prev, nodes: updatedNodes, edges: updatedEdges };
    });
    if (selectedNode?.id === id) setSelectedNode(null);
  };

  const deleteEdge = (id) => {
    setWorkflow((prev) => ({
      ...prev,
      edges: (prev.edges || []).filter((e) => e.id !== id),
    }));
    if (selectedEdge?.id === id) setSelectedEdge(null);
  };

  const handleStartConnect = (sourceNode) => {
    setConnectingSource(sourceNode);
  };

  const handleEndConnect = (targetNode) => {
    if (connectingSource && connectingSource.id !== targetNode.id) {
      const newEdge = {
        id: `e_${connectingSource.id}_${targetNode.id}`,
        source: connectingSource.id,
        target: targetNode.id,
      };

      setWorkflow((prev) => {
        const edgeExists = (prev.edges || []).some(
          (e) => e.source === newEdge.source && e.target === newEdge.target
        );
        if (edgeExists) return prev;
        const updatedEdges = [...(prev.edges || []), newEdge];
        const { valid, errors } = validateGraphLocally(prev.nodes || [], updatedEdges);
        setIsValid(valid);
        setValidationErrors(errors);
        return { ...prev, edges: updatedEdges };
      });
    }
    setConnectingSource(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    try {
      const rawData = e.dataTransfer.getData('application/neurodesk-node') || e.dataTransfer.getData('text/plain');
      if (!rawData) return;
      const { type, label } = JSON.parse(rawData);

      let position = { x: 300 + Math.random() * 50, y: 200 + Math.random() * 50 };
      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        position = {
          x: Math.max(20, Math.round(e.clientX - rect.left - 128)),
          y: Math.max(20, Math.round(e.clientY - rect.top - 30)),
        };
      }
      addNodeAtPosition(type, label, position);
    } catch (err) {
      console.error('Failed to handle dropped node:', err);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      if (workflow.id) {
        const updated = await workflowService.updateWorkflow(workflow.id, {
          name: workflow.name,
          description: workflow.description,
          status: workflow.status,
          nodes: workflow.nodes || [],
          edges: workflow.edges || [],
          variables: workflow.variables || {},
        });
        setWorkflow(updated);
      } else {
        const created = await workflowService.createWorkflow({
          name: workflow.name,
          description: workflow.description,
          nodes: workflow.nodes || [],
          edges: workflow.edges || [],
          variables: workflow.variables || {},
        });
        setWorkflow(created);
      }
    } catch (err) {
      console.error('Failed to save workflow:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRunExecution = async () => {
    setIsRunning(true);
    setShowConsole(true);
    try {
      let wfId = workflow.id;
      if (!wfId) {
        const saved = await workflowService.createWorkflow({
          name: workflow.name,
          description: workflow.description,
          nodes: workflow.nodes || [],
          edges: workflow.edges || [],
          variables: workflow.variables || {},
        });
        wfId = saved.id;
        setWorkflow(saved);
      } else {
        await workflowService.updateWorkflow(wfId, {
          nodes: workflow.nodes || [],
          edges: workflow.edges || [],
          variables: workflow.variables || {},
        });
      }

      const execRes = await workflowService.runWorkflow(wfId, { inputs: {} });
      setCurrentExecution(execRes);
      setExecutions((prev) => [execRes, ...prev]);
    } catch (err) {
      console.error('Workflow execution failed:', err);
    } finally {
      setIsRunning(false);
    }
  };

  const handleDuplicate = async () => {
    if (!workflow.id) return;
    try {
      const dup = await workflowService.duplicateWorkflow(workflow.id);
      setWorkflow(dup);
    } catch (err) {
      console.error('Failed to duplicate workflow:', err);
    }
  };

  const handleLoadTemplate = (templateId) => {
    const tmpl = templates.find((t) => t.id === templateId);
    if (tmpl) {
      setWorkflow((prev) => ({
        ...prev,
        name: tmpl.name,
        description: tmpl.description,
        nodes: tmpl.nodes,
        edges: tmpl.edges,
      }));
      const { valid, errors } = validateGraphLocally(tmpl.nodes, tmpl.edges);
      setIsValid(valid);
      setValidationErrors(errors);
    }
  };

  return (
    <div className="h-screen w-full bg-slate-950 flex flex-col overflow-hidden text-slate-100 font-sans select-none">
      {/* Top Studio Toolbar */}
      <WorkflowToolbar
        workflow={workflow}
        isValid={isValid}
        validationErrors={validationErrors}
        isRunning={isRunning}
        templates={templates}
        onRun={handleRunExecution}
        onSave={handleSave}
        onLoadTemplate={handleLoadTemplate}
        onDuplicate={handleDuplicate}
        onToggleConsole={() => setShowConsole(!showConsole)}
        onToggleHistory={() => setShowHistory(!showHistory)}
        onToggleMiniMap={() => setShowMiniMap(!showMiniMap)}
        onBack={onBack}
        showConsole={showConsole}
        showHistory={showHistory}
        showMiniMap={showMiniMap}
      />

      {/* Main Workspace Row */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Drag & Drop Sidebar */}
        <WorkflowSidebar onAddNode={addNode} />

        {/* Center Interactive SVG/HTML Graph Canvas */}
        <div
          ref={canvasRef}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => {
            setSelectedNode(null);
            setSelectedEdge(null);
            setConnectingSource(null);
          }}
          className="flex-1 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:24px_24px] bg-slate-950 relative overflow-hidden cursor-grab active:cursor-grabbing"
        >
          {/* SVG Connecting Edges Layer */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="#475569" />
              </marker>
            </defs>

            {(workflow.edges || []).map((edge) => {
              const sourceNode = (workflow.nodes || []).find((n) => n.id === edge.source);
              const targetNode = (workflow.nodes || []).find((n) => n.id === edge.target);
              return (
                <WorkflowEdge
                  key={edge.id}
                  edge={edge}
                  sourceNode={sourceNode}
                  targetNode={targetNode}
                  isSelected={selectedEdge?.id === edge.id}
                  isExecuting={isRunning}
                  onSelect={(e) => setSelectedEdge(e)}
                  onDelete={deleteEdge}
                />
              );
            })}
          </svg>

          {/* HTML Interactive Nodes Layer */}
          {(workflow.nodes || []).map((node) => {
            const execNodeState = currentExecution?.nodes?.find((n) => n.node_id === node.id);
            return (
              <WorkflowNode
                key={node.id}
                node={node}
                isSelected={selectedNode?.id === node.id}
                executionState={execNodeState}
                onSelect={(n) => setSelectedNode(n)}
                onDelete={deleteNode}
                onConfigure={(n) => setSelectedNode(n)}
                onStartConnect={handleStartConnect}
                onEndConnect={handleEndConnect}
                onNodeMove={moveNode}
              />
            );
          })}

          {/* Overlay MiniMap */}
          {showMiniMap && (
            <div className="absolute bottom-4 left-4 z-20">
              <MiniMap nodes={workflow.nodes || []} edges={workflow.edges || []} />
            </div>
          )}
        </div>

        {/* Right Drawer: Properties Panel */}
        {selectedNode && (
          <NodePropertiesPanel
            node={selectedNode}
            onUpdateNode={updateNode}
            onClose={() => setSelectedNode(null)}
          />
        )}

        {/* Right Drawer: Execution History */}
        {showHistory && (
          <ExecutionHistoryPanel
            executions={executions}
            onSelectExecution={(exec) => {
              setCurrentExecution(exec);
              setShowConsole(true);
            }}
            onClose={() => setShowHistory(false)}
          />
        )}
      </div>

      {/* Bottom Execution Console Drawer */}
      {showConsole && (
        <ExecutionConsole
          execution={currentExecution}
          onClose={() => setShowConsole(false)}
        />
      )}
    </div>
  );
};

export default WorkflowCanvas;
