from __future__ import annotations
import argparse, json, sys
from .core import RagError, build_index, format_context, load_index, search, validate_index
from . import __version__

def parser():
    p=argparse.ArgumentParser(prog="local-rag",description="Local source-grounded BM25 retrieval workspace")
    p.add_argument("--version",action="version",version=f"Local RAG Desk {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub=p.add_subparsers(dest="command",required=True)
    ix=sub.add_parser("index",help="build an index"); ix.add_argument("root"); ix.add_argument("-o","--output",default=".rag/index.json"); ix.add_argument("--chunk-size",type=int,default=180); ix.add_argument("--overlap",type=int,default=30)
    for name in ("search","context"):
        q=sub.add_parser(name,help=f"{name} local documents"); q.add_argument("query"); q.add_argument("-i","--index",default=".rag/index.json"); q.add_argument("-k","--limit",type=int,default=5)
        if name=="search": q.add_argument("--json",action="store_true")
    va=sub.add_parser("validate",help="validate index structure"); va.add_argument("-i","--index",default=".rag/index.json")
    return p

def main(argv=None):
    args=parser().parse_args(argv)
    try:
        if args.command=="index":
            idx=build_index(args.root,args.output,chunk_size=args.chunk_size,overlap=args.overlap); print(f"Indexed {idx['chunk_count']} chunks from {idx['file_count']} files -> {args.output}")
        elif args.command=="validate":
            idx=load_index(args.index); validate_index(idx); print(f"Valid index: {idx['chunk_count']} chunks from {idx['file_count']} files")
        else:
            hits=search(load_index(args.index),args.query,limit=args.limit)
            if args.command=="context": print(format_context(hits))
            elif args.json: print(json.dumps([h.as_dict() for h in hits],ensure_ascii=False,indent=2))
            elif not hits: print("No relevant local context found.")
            else:
                for n,h in enumerate(hits,1): print(f"{n}. {h.source}:{h.start_line}-{h.end_line}  score={h.score:.3f}\n   {h.text.replace(chr(10),' ')[:240]}")
        return 0
    except RagError as exc:
        print(f"error: {exc}",file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
