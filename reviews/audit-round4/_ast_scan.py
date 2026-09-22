
# -*- coding: utf-8 -*-
import ast, sys
src = open("handler.py", encoding="utf-8").read()
tree = ast.parse(src)
assigned = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                assigned.add(t.id)
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        assigned.add(node.target.id)
used = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        used.add(node.id)
    if isinstance(node, ast.Attribute):
        pass
dunder = {n for n in assigned if n.startswith("__")}
dead = sorted(assigned - used - dunder)
print("DEAD module-level constants:", dead)
# functions defined but never referenced (module level), excluding entrypoints
fns = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
fnrefs = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        fnrefs.add(node.id)
print("UNUSED functions:", [f for f in fns if f not in fnrefs and f != "on_pre_tool_call"])
# GUARDS order from AST (list literal in assignment)
for node in tree.body:
    if isinstance(node, ast.Assign) and any(getattr(t,"id","")== "GUARDS" for t in node.targets):
        print("GUARDS order:", [e.id for e in node.value.elts])
