"""Export Mermaid Diagrams for BidGraph and ConversationGraph."""

import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph

docs_img = Path(__file__).resolve().parents[1] / "docs" / "images"
docs_img.mkdir(parents=True, exist_ok=True)

bg = build_bid_graph()
cg = build_conversation_graph()

bg_mermaid = bg.get_graph().draw_mermaid()
cg_mermaid = cg.get_graph().draw_mermaid()

(docs_img / "bid_graph.mmd").write_text(bg_mermaid, encoding="utf-8")
(docs_img / "conversation_graph.mmd").write_text(cg_mermaid, encoding="utf-8")

# Also write clean readable markdown visualization file
md_content = f"""# System Graph Visualizations

## 1. BidGraph (Autonomous Intake, Risk, Match, Pricing, Writer, Verifier, Critic, Compliance & Human Approval)
```mermaid
{bg_mermaid}
```

## 2. ConversationGraph (Client Liaison, Scope Creep & Gate)
```mermaid
{cg_mermaid}
```
"""

(docs_img / "GRAPHS.md").write_text(md_content, encoding="utf-8")
print(f"Graph diagrams exported successfully to {docs_img}")
