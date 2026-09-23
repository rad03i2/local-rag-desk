from __future__ import annotations
import json, math, re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)

class RagError(ValueError): pass

@dataclass(frozen=True)
class SearchHit:
    source: str
    start_line: int
    end_line: int
    text: str
    score: float
    def as_dict(self):
        return {"source": self.source, "start_line": self.start_line, "end_line": self.end_line, "text": self.text, "score": round(self.score, 6)}

def tokenize(text: str) -> list[str]:
    return [x.group(0).casefold() for x in TOKEN_RE.finditer(text)]

def _chunks(text: str, source: str, size: int, overlap: int):
    lines=text.splitlines(); words=[]
    for n,line in enumerate(lines,1):
        words.extend((m.group(0),n) for m in TOKEN_RE.finditer(line))
    out=[]; step=size-overlap
    for start in range(0,len(words),step):
        part=words[start:start+size]
        if not part: break
        first,last=part[0][1],part[-1][1]; body="\n".join(lines[first-1:last]).strip(); tokens=tokenize(body)
        if tokens: out.append({"source":source,"start_line":first,"end_line":last,"text":body,"tokens":tokens,"length":len(tokens)})
        if start+size>=len(words): break
    return out

def build_index(root, output=None, *, chunk_size=180, overlap=30):
    if chunk_size < 20 or overlap < 0 or overlap >= chunk_size: raise RagError("invalid chunk size/overlap")
    base=Path(root).expanduser().resolve()
    if not base.is_dir(): raise RagError("document root is not a directory")
    chunks=[]; files=0
    for path in sorted(base.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in {".txt",".md"}: continue
        try: text=path.read_text(encoding="utf-8")
        except (OSError,UnicodeDecodeError) as exc: raise RagError(f"cannot read {path}: {exc}") from exc
        chunks += _chunks(text,path.relative_to(base).as_posix(),chunk_size,overlap); files+=1
    if not chunks: raise RagError("no indexable UTF-8 .txt/.md text found")
    df=Counter()
    for c in chunks: df.update(set(c["tokens"]))
    index={"format":1,"root_name":base.name,"file_count":files,"chunk_count":len(chunks),"chunk_size":chunk_size,"overlap":overlap,"avg_length":sum(c["length"] for c in chunks)/len(chunks),"document_frequency":dict(df),"chunks":chunks}
    validate_index(index)
    if output:
        dest=Path(output).expanduser(); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    return index

def validate_index(index):
    if not isinstance(index,dict) or index.get("format")!=1: raise RagError("unsupported index format")
    chunks=index.get("chunks")
    if not isinstance(chunks,list) or not chunks or index.get("chunk_count")!=len(chunks): raise RagError("invalid chunk metadata")
    if not isinstance(index.get("document_frequency"),dict) or not isinstance(index.get("avg_length"),(int,float)): raise RagError("invalid statistics")
    for c in chunks:
        if not isinstance(c,dict) or not {"source","start_line","end_line","text","tokens","length"}.issubset(c): raise RagError("malformed chunk")
        if not isinstance(c["tokens"],list) or c["length"]!=len(c["tokens"]): raise RagError("invalid chunk tokens")

def load_index(path):
    try: data=json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: raise RagError(f"cannot load index: {exc}") from exc
    validate_index(data); return data

def search(index, query, *, limit=5, k1=1.5, b=0.75):
    validate_index(index); terms=tokenize(query)
    if not terms: raise RagError("query must contain searchable text")
    if not 1<=limit<=100: raise RagError("limit must be 1..100")
    n=len(index["chunks"]); avg=float(index["avg_length"]); df=index["document_frequency"]; hits=[]
    for c in index["chunks"]:
        counts=Counter(c["tokens"]); score=0.0
        for term in terms:
            freq=counts.get(term,0)
            if freq:
                d=int(df.get(term,0)); idf=math.log(1+(n-d+0.5)/(d+0.5)); denom=freq+k1*(1-b+b*c["length"]/avg); score += idf*(freq*(k1+1)/denom)
        if score>0: hits.append(SearchHit(c["source"],c["start_line"],c["end_line"],c["text"],score))
    return sorted(hits,key=lambda h:(-h.score,h.source,h.start_line))[:limit]

def format_context(hits):
    if not hits: return "No relevant local context found."
    return "\n\n".join(f"[Source {i}: {h.source}:{h.start_line}-{h.end_line}]\n{h.text}" for i,h in enumerate(hits,1))
