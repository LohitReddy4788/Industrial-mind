"""
Graph query engine + pyvis visualization renderer.
"""

from pathlib import Path
from typing import List, Dict, Optional

from app.graph_builder import GraphBuilder


# ─── Color map for node types ─────────────────────────────────────────────────

NODE_COLORS = {
    "Equipment":  "#3b82f6",   # blue
    "Incident":   "#ef4444",   # red
    "Regulation": "#22c55e",   # green
    "Procedure":  "#f59e0b",   # amber
    "Person":     "#a855f7",   # purple
    "Document":   "#64748b",   # slate
    "FailureMode":"#f97316",   # orange
}

NODE_SIZES = {
    "Equipment":  30,
    "Incident":   25,
    "Regulation": 25,
    "Procedure":  22,
    "Person":     18,
    "Document":   15,
    "FailureMode":20,
}


class GraphVisualizer:
    """Renders pyvis interactive graph HTML."""

    def build_pyvis(self, nodes: List[Dict], edges: List[Dict],
                    height: str = "600px") -> Optional[object]:
        """Build a pyvis Network from nodes and edges."""
        try:
            from pyvis.network import Network
        except ImportError:
            print("[WARN] pyvis not installed")
            return None

        net = Network(height=height, width="100%", bgcolor="#f8fafc",
                      font_color="#334155", directed=True)
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 150
            },
            "solver": "forceAtlas2Based",
            "stabilization": { "iterations": 150 }
          },
          "edges": {
            "color": { "color": "#cbd5e1" },
            "font": { "size": 10, "color": "#64748b" },
            "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
          },
          "nodes": {
            "font": { "size": 12, "color": "#0f172a" },
            "borderWidth": 1.5,
            "borderWidthSelected": 3
          }
        }
        """)

        added_nodes = set()
        for node in nodes:
            node_id = str(node.get("id") or node.get("filename") or "?")
            if node_id in added_nodes:
                continue
            added_nodes.add(node_id)
            label = node.get("label", "Unknown")
            color = NODE_COLORS.get(label, "#6b7280")
            size = NODE_SIZES.get(label, 20)
            title = f"{label}: {node_id}"
            net.add_node(node_id, label=node_id[:20], title=title,
                         color=color, size=size)

        for edge in edges:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            rel = edge.get("rel_type", "")
            if src in added_nodes and tgt in added_nodes:
                net.add_edge(src, tgt, title=rel, label=rel[:15])

        return net

    def render_to_html(self, nodes: List[Dict], edges: List[Dict],
                       output_path: str = "graph.html") -> str:
        """Save graph as HTML file and return path."""
        net = self.build_pyvis(nodes, edges)
        if net is None:
            return ""
        net.save_graph(output_path)
        return output_path

    def get_html_string(self, nodes: List[Dict], edges: List[Dict]) -> str:
        """Return the graph HTML as a string for Streamlit embedding."""
        import os
        net = self.build_pyvis(nodes, edges)
        if net is None:
            return "<p>Graph visualization not available (pyvis not installed).</p>"
        # Use a fixed path under ./data/ — avoids Windows tempfile locking issues
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = str(data_dir / "_graph_tmp.html")
        try:
            net.save_graph(tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                html = f.read()
            return html
        except Exception as e:
            return f"<p>Graph error: {e}</p>"
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


class GraphQueryEngine:
    """High-level query methods over the knowledge graph."""

    def __init__(self, graph_builder: GraphBuilder = None):
        self.gb = graph_builder or GraphBuilder()
        self.viz = GraphVisualizer()

    def get_full_graph_html(self) -> str:
        data = self.gb.get_all_for_visualization()
        return self.viz.get_html_string(data["nodes"], data["edges"])

    def get_equipment_subgraph_html(self, equipment_id: str) -> str:
        data = self.gb.get_equipment_subgraph(equipment_id)
        return self.viz.get_html_string(data["nodes"], data["edges"])

    def get_high_risk_equipment(self) -> List[Dict]:
        return self.gb.find_high_risk_equipment()

    def get_graph_stats(self) -> Dict:
        return self.gb.get_stats()

    def get_legend(self) -> Dict:
        return {label: color for label, color in NODE_COLORS.items()}
