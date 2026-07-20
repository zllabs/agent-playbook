import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
  MarkerType,
} from "@xyflow/react";

import type { Playbook } from "../types";

interface Props {
  playbook: Playbook;
  onNodeSelect?: (id: string) => void;
}

export default function SkillGraph({ playbook, onNodeSelect }: Props) {
  const { nodes, edges } = layoutGraph(playbook);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onNodeSelect?.(node.id);
    },
    [onNodeSelect],
  );

  if (playbook.skills.length === 0) return null;

  return (
    <div className="graph-panel">
      <h2 className="section-title">Skill graph</h2>
      {edges.length === 0 && playbook.skills.length > 0 && (
        <p className="graph-note">No catalog edges between selected skills — showing isolated nodes.</p>
      )}
      <div className="graph-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={onNodeClick}
          fitView
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable
          proOptions={{ hideAttribution: true }}
        >
          <Background gap={16} size={1} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}

function layoutGraph(playbook: Playbook): { nodes: Node[]; edges: Edge[] } {
  const skillIds = new Set(playbook.skills.map((s) => s.id));

  const flowEdges: Edge[] = playbook.edges
    .filter((e) => skillIds.has(e.from) && skillIds.has(e.to))
    .map((e, i) => ({
      id: `e-${i}`,
      source: e.from,
      target: e.to,
      label: e.type.replace("_", " "),
      type: "smoothstep",
      markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
      className: e.type === "requires" ? "edge-requires" : "edge-related",
    }));

  const cols = Math.ceil(Math.sqrt(playbook.skills.length));
  const gapX = 220;
  const gapY = 100;

  const nodes: Node[] = playbook.skills.map((skill, i) => ({
    id: skill.id,
    data: { label: skill.title },
    position: {
      x: (i % cols) * gapX,
      y: Math.floor(i / cols) * gapY,
    },
    className: "skill-node",
  }));

  return { nodes, edges: flowEdges };
}
