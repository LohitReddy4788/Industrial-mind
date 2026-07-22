"""
Knowledge graph builder.
Uses Neo4j when configured, falls back to NetworkX in-memory with JSON persistence.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

from app.config import USE_NEO4J, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

GRAPH_PERSIST_PATH = Path(__file__).resolve().parent.parent / "data" / "graph.json"


# ─── Neo4j backend ────────────────────────────────────────────────────────────

class Neo4jGraph:
    def __init__(self):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Verify connection is actually reachable (driver() is lazy)
        with self.driver.session() as s:
            s.run("RETURN 1")
        self._create_constraints()

    def _create_constraints(self):
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Equipment) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Regulation) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Procedure) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.filename IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (f:FailureMode) REQUIRE f.name IS UNIQUE",
        ]
        with self.driver.session() as s:
            for q in queries:
                try:
                    s.run(q)
                except Exception:
                    pass

    def run(self, query: str, params: Dict = None):
        with self.driver.session() as s:
            return list(s.run(query, params or {}))

    def close(self):
        self.driver.close()


# ─── NetworkX fallback with JSON persistence ─────────────────────────────────

class NetworkXGraph:
    def __init__(self):
        import networkx as nx
        self.G = nx.DiGraph()
        self._node_data: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        """Restore graph from disk if snapshot exists."""
        if not GRAPH_PERSIST_PATH.exists():
            return
        try:
            import networkx as nx
            data = json.loads(GRAPH_PERSIST_PATH.read_text(encoding="utf-8"))
            for n in data.get("nodes", []):
                nid = n["id"]
                self.G.add_node(nid, **{k: v for k, v in n.items() if k != "id"})
                self._node_data[nid] = n
            for e in data.get("edges", []):
                src, tgt = e["source"], e["target"]
                if src in self.G and tgt in self.G:
                    self.G.add_edge(src, tgt, rel_type=e.get("rel_type", ""))
        except Exception as ex:
            print(f"[Graph] Could not load snapshot: {ex}")

    def save(self):
        """Persist graph to disk."""
        GRAPH_PERSIST_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "nodes": [{"id": n, **self.G.nodes[n]} for n in self.G.nodes()],
            "edges": [{"source": s, "target": t, **d}
                      for s, t, d in self.G.edges(data=True)],
        }
        GRAPH_PERSIST_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_node(self, node_id: str, label: str, **props):
        self.G.add_node(node_id, label=label, **props)
        self._node_data[node_id] = {"label": label, **props}

    def add_edge(self, src: str, dst: str, rel_type: str):
        if src in self.G and dst in self.G:
            self.G.add_edge(src, dst, rel_type=rel_type)

    def get_stats(self) -> Dict:
        from collections import Counter
        labels = Counter(d.get("label") for _, d in self.G.nodes(data=True))
        return {
            "nodes": self.G.number_of_nodes(),
            "relationships": self.G.number_of_edges(),
            "by_label": dict(labels),
        }

    def get_neighbors(self, node_id: str) -> List[Dict]:
        results = []
        for _, nbr, data in self.G.out_edges(node_id, data=True):
            results.append({"source": node_id, "target": nbr,
                            "rel_type": data.get("rel_type", ""),
                            "props": self._node_data.get(nbr, {})})
        for src, _, data in self.G.in_edges(node_id, data=True):
            results.append({"source": src, "target": node_id,
                            "rel_type": data.get("rel_type", ""),
                            "props": self._node_data.get(src, {})})
        return results

    def get_all_nodes(self) -> List[Dict]:
        return [{"id": n, **self.G.nodes[n]} for n in self.G.nodes()]

    def get_all_edges(self) -> List[Dict]:
        return [{"source": s, "target": t, **d}
                for s, t, d in self.G.edges(data=True)]

    def find_high_risk_equipment(self) -> List[Dict]:
        results = []
        for eq, d in self.G.nodes(data=True):
            if d.get("label") != "Equipment":
                continue
            incidents = [n for n in self.G.successors(eq)
                         if self.G.nodes[n].get("label") == "Incident"]
            failures  = [n for n in self.G.successors(eq)
                         if self.G.nodes[n].get("label") == "FailureMode"]
            risk = len(incidents) * 2 + len(failures)
            results.append({
                "equipment_id": eq,
                "incident_count": len(incidents),
                "failure_mode_count": len(failures),
                "risk_score": risk,
            })
        return sorted(results, key=lambda x: x["risk_score"], reverse=True)


# ─── Unified GraphBuilder ─────────────────────────────────────────────────────

class GraphBuilder:
    def __init__(self):
        if USE_NEO4J:
            try:
                self._backend = Neo4jGraph()
                self._mode = "neo4j"
            except Exception as e:
                print(f"[WARN] Neo4j failed ({e}). Falling back to NetworkX.")
                self._backend = NetworkXGraph()
                self._mode = "networkx"
        else:
            self._backend = NetworkXGraph()
            self._mode = "networkx"

    @property
    def mode(self) -> str:
        return self._mode

    def _add_node(self, label: str, node_id: str, props: Dict):
        if self._mode == "neo4j":
            props_str = ", ".join(f"n.{k} = ${k}" for k in props)
            q = (f"MERGE (n:{label} {{id: $id}}) SET {props_str}"
                 if props_str else f"MERGE (n:{label} {{id: $id}})")
            self._backend.run(q, {"id": node_id, **props})
        else:
            # strip 'id' from props to avoid duplicate keyword argument
            safe_props = {k: v for k, v in props.items() if k != "id"}
            self._backend.add_node(node_id, label=label, **safe_props)

    def _add_rel(self, from_label: str, from_id: str,
                 rel: str, to_label: str, to_id: str):
        if self._mode == "neo4j":
            q = (f"MATCH (a:{from_label} {{id: $fid}}), (b:{to_label} {{id: $tid}}) "
                 f"MERGE (a)-[:{rel}]->(b)")
            self._backend.run(q, {"fid": from_id, "tid": to_id})
        else:
            self._backend.add_edge(from_id, to_id, rel_type=rel)

    def build_from_entities(self, entities: List[Dict], chunks: List[Dict]):
        """Populate graph from extracted entities. Saves to disk when done."""
        file_types: Dict[str, str] = {
            c["source_file"]: c["doc_type"] for c in chunks
        }

        for source_file, doc_type in file_types.items():
            filename = Path(source_file).name
            self._add_node("Document", filename, {
                "filename": filename, "doc_type": doc_type, "path": source_file,
            })

        for ent in entities:
            source_file = ent.get("source_file", "")
            filename = Path(source_file).name
            doc_type = ent.get("doc_type", "general")

            for eq_id in ent.get("equipment_ids", []):
                self._add_node("Equipment", eq_id, {"id": eq_id, "name": f"Equipment {eq_id}"})
                self._add_rel("Document", filename, "MENTIONS", "Equipment", eq_id)

            for fm in ent.get("failure_modes", []):
                fm_id = fm.replace(" ", "_")
                self._add_node("FailureMode", fm_id, {"id": fm_id, "name": fm})
                for eq_id in ent.get("equipment_ids", []):
                    self._add_rel("Equipment", eq_id, "EXPERIENCED", "FailureMode", fm_id)

            for reg in ent.get("regulation_refs", []):
                reg_id = reg["code"]
                self._add_node("Regulation", reg_id, {
                    "id": reg_id,
                    "standard_name": reg["standard_name"],
                    "number": reg["number"],
                })
                self._add_rel("Document", filename, "REFERENCES", "Regulation", reg_id)

            if doc_type == "incidents":
                inc_id = f"INC_{filename}"
                dates = ent.get("dates", [])
                date_str = dates[0]["date_normalized"] if dates else "unknown"
                self._add_node("Incident", inc_id, {
                    "id": inc_id,
                    "severity": ent.get("severity", "Medium"),
                    "date": date_str,
                    "document": filename,
                })
                self._add_rel("Document", filename, "DOCUMENTS", "Incident", inc_id)
                for eq_id in ent.get("equipment_ids", []):
                    self._add_rel("Equipment", eq_id, "HAD_INCIDENT", "Incident", inc_id)
                for reg in ent.get("regulation_refs", []):
                    self._add_rel("Incident", inc_id, "VIOLATED", "Regulation", reg["code"])

            if doc_type == "procedures":
                proc_id = f"PROC_{filename}"
                self._add_node("Procedure", proc_id, {
                    "id": proc_id, "name": filename, "document": filename,
                })
                self._add_rel("Document", filename, "CONTAINS_PROCEDURE", "Procedure", proc_id)
                for eq_id in ent.get("equipment_ids", []):
                    self._add_rel("Procedure", proc_id, "GOVERNS", "Equipment", eq_id)
                for reg in ent.get("regulation_refs", []):
                    self._add_rel("Regulation", reg["code"], "REQUIRES", "Procedure", proc_id)

            for person in ent.get("people", []):
                p_id = person.replace(" ", "_")
                self._add_node("Person", p_id, {"id": p_id, "name": person})
                if doc_type == "incidents":
                    self._add_rel("Person", p_id, "INVESTIGATED", "Incident", f"INC_{filename}")

        # Persist after every build
        if self._mode == "networkx":
            self._backend.save()

        return self.get_stats()

    def get_stats(self) -> Dict:
        if self._mode == "neo4j":
            try:
                res = self._backend.run(
                    "MATCH (n) RETURN labels(n)[0] as label, count(n) as cnt"
                )
                by_label = {r["label"]: r["cnt"] for r in res}
                rel_res = self._backend.run("MATCH ()-[r]->() RETURN count(r) as cnt")
                total_rels = rel_res[0]["cnt"] if rel_res else 0
                return {"nodes": sum(by_label.values()),
                        "relationships": total_rels, "by_label": by_label}
            except Exception as e:
                return {"nodes": 0, "relationships": 0, "by_label": {}, "error": str(e)}
        return self._backend.get_stats()

    def get_all_for_visualization(self) -> Dict:
        if self._mode == "networkx":
            return {"nodes": self._backend.get_all_nodes(),
                    "edges": self._backend.get_all_edges()}
        try:
            node_res = self._backend.run(
                "MATCH (n) RETURN n.id as id, labels(n)[0] as label, "
                "properties(n) as props LIMIT 200"
            )
            edge_res = self._backend.run(
                "MATCH (a)-[r]->(b) RETURN a.id as source, b.id as target, "
                "type(r) as rel_type LIMIT 500"
            )
            nodes = [{"id": r["id"], "label": r["label"], **r["props"]} for r in node_res]
            edges = [{"source": r["source"], "target": r["target"],
                      "rel_type": r["rel_type"]} for r in edge_res]
            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            return {"nodes": [], "edges": [], "error": str(e)}

    def get_equipment_subgraph(self, equipment_id: str) -> Dict:
        if self._mode == "networkx":
            neighbors = self._backend.get_neighbors(equipment_id)
            eq_node = self._backend._node_data.get(equipment_id, {})
            nodes = [{"id": equipment_id, "label": "Equipment", **eq_node}]
            edges = []
            seen_nodes = {equipment_id}
            for n in neighbors:
                neighbor_id = n["target"] if n["source"] == equipment_id else n["source"]
                if neighbor_id not in seen_nodes:
                    nodes.append({"id": neighbor_id, **n["props"]})
                    seen_nodes.add(neighbor_id)
                edges.append({"source": n["source"], "target": n["target"],
                               "rel_type": n["rel_type"]})
            return {"nodes": nodes, "edges": edges}
        try:
            result = self._backend.run("""
                MATCH (eq:Equipment {id: $id})-[r]-(n)
                RETURN eq, r, n LIMIT 100
            """, {"id": equipment_id})
            nodes_map, edges = {}, []
            for rec in result:
                for key in ["eq", "n"]:
                    node = rec.get(key)
                    if node:
                        nid = node.get("id", str(node.id))
                        nodes_map[nid] = dict(node)
            return {"nodes": list(nodes_map.values()), "edges": edges}
        except Exception as e:
            return {"nodes": [], "edges": [], "error": str(e)}

    def find_high_risk_equipment(self) -> List[Dict]:
        if self._mode == "networkx":
            return self._backend.find_high_risk_equipment()
        try:
            result = self._backend.run("""
                MATCH (e:Equipment)
                OPTIONAL MATCH (e)-[:HAD_INCIDENT]->(i:Incident)
                OPTIONAL MATCH (e)-[:EXPERIENCED]->(f:FailureMode)
                RETURN e.id as equipment_id,
                       count(DISTINCT i) as incident_count,
                       count(DISTINCT f) as failure_mode_count
                ORDER BY incident_count DESC LIMIT 10
            """)
            return [{"equipment_id": r["equipment_id"],
                     "incident_count": r["incident_count"],
                     "failure_mode_count": r["failure_mode_count"],
                     "risk_score": r["incident_count"] * 2 + r["failure_mode_count"]}
                    for r in result]
        except Exception:
            return []

    def clear(self):
        if self._mode == "neo4j":
            self._backend.run("MATCH (n) DETACH DELETE n")
        else:
            import networkx as nx
            self._backend.G = nx.DiGraph()
            self._backend._node_data = {}
            if GRAPH_PERSIST_PATH.exists():
                GRAPH_PERSIST_PATH.unlink()
