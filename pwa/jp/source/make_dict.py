#!/usr/bin/env python3
"""Turns SKK-JISYO.L (GPL v2+, SKK Development Team) into dict-ja.txt for Plainwrite-J.
Lines: reading<TAB>cand/cand/...   Okuri-ari readings end in a romaji consonant (かk = 書く).
Lisp expressions and number templates are dropped; each reading keeps at most MAX candidates."""
import sys,re
MAX=int(sys.argv[3]) if len(sys.argv)>3 else 16
txt=open(sys.argv[1],'rb').read().decode('euc_jis_2004',errors='replace')
# readings in the medium dictionary (SKK-JISYO.M) count as common words, which the converter prefers
COMMON={}
if len(sys.argv)>4:
    for l in open(sys.argv[4],'rb').read().decode('euc_jis_2004',errors='replace').split('\n'):
        if l and not l.startswith(';'):
            k,_,v=l.partition(' /');COMMON[k]=[x.split(';')[0] for x in v.strip('/').split('/') if x and '(' not in x]
out=[];mode=None
for l in txt.split('\n'):
    if l.startswith(';; okuri-ari'):mode='ari';continue
    if l.startswith(';; okuri-nasi'):mode='nasi';continue
    if not l or l.startswith(';'):continue
    k,_,v=l.partition(' /')
    if not re.fullmatch(r'[ぁ-ゖーゔ]+[a-z]?',k):continue   # kana readings only (no abbrev/number entries)
    if '#' in k: continue
    c=[x.split(';')[0] for x in v.strip('/').split('/')]
    c=[x for x in c if x and '(' not in x and '\t' not in x and '�' not in x and '[' not in x]
    seen=[];[seen.append(x) for x in c if x not in seen]
    if not seen:continue
    out.append(k+'\t'+('*' if k in COMMON else '')+'/'.join(seen[:MAX]))
open(sys.argv[2],'w',encoding='utf-8').write('\n'.join(out)+'\n')
print(len(out))
