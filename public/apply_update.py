#!/usr/bin/env python3
"""Usage: python3 apply_update.py path/to/index.html path/to/admin.html
Backs up both files (.bak), then applies the update. Stops with an error if a file doesn't match."""
import sys, shutil

def rep(s, old, new):
    assert s.count(old) == 1, "Anchor not found exactly once: " + old[:60]
    return s.replace(old, new)

ARABIC_CSS = r'''/* ===== readable Arabic ===== */
.panel .ar{font-size:2rem;line-height:1.7}
td:first-child .ar{font-size:1.65rem;line-height:1.4;color:var(--ink);opacity:.9}
tr.nxt td:first-child .ar{opacity:1}
.jum .ar{font-size:1.5rem;line-height:1.5}
.it .a{font-size:2.1em;line-height:1.9}
.verse{line-height:1.9;font-weight:700}
.off{display:none!important}
/* ===== layouts ===== */'''

NEW_CSS = r'''
@media (orientation:landscape){
 html[data-layout=bottom] #screen{grid-template-columns:1fr;grid-template-rows:1fr auto auto}
 html[data-layout=bottom] .panel{grid-row:2;flex-direction:row;justify-content:space-around;padding:.5rem 1rem}
 html[data-layout=bottom] .main{grid-row:1}
 html[data-layout=bottom] footer{grid-column:1;grid-row:3}
 html[data-layout=bottom] #clk{width:7rem}
 html[data-layout=bottom] .name{font-size:1.9rem}
 html[data-layout=bottom] #time{font-size:3.6rem}
 html[data-layout=bottom] #ncount{font-size:2.6rem}
 html[data-layout=wideright] #screen{grid-template-columns:1.5fr .78fr}
 html[data-layout=wideright] .panel{grid-column:2;grid-row:1/3}
 html[data-layout=wideright] .main{grid-column:1;grid-row:1}
 html[data-layout=wideright] footer{grid-column:1;grid-row:2}
 html:is([data-layout=wide],[data-layout=wideright]) .main{grid-template-columns:1.15fr 1fr;column-gap:1.2rem}
}
/* more themes */
html[data-theme=midnight]{--bg:#0a0f1f;--paper:#121a33;--ink:#f1ecd9;--mut:#a9b1c9;--green:#e3b95b;--brass:#e3b95b;--sand:#2a3556;--tint:#1a2447;--pbg:#101833;--pfg:#f1ecd9;--pacc:#e3b95b;--pline:rgba(227,185,91,.35);--nbg:#e3b95b;--nfg:#0a0f1f;--nacc:#0a0f1f;--jc:#f4d98a;--hd:#f4d98a;--fbg:#060a16;--ffg:#f1ecd9;--chgfg:#0a0f1f;--cface:#121a33;--crim:#e3b95b;--ctick:#e3b95b;--cnum:#f1ecd9;--chh:#f1ecd9;--cmh:#e3b95b;--csh:#fff;--pat:none}
html[data-theme=desert]{--bg:#f4e4c8;--paper:#fff6e3;--ink:#3a2412;--mut:#7a5a3c;--green:#9a3f1d;--brass:#b8651b;--sand:#e0c598;--tint:#f0d9aa;--pbg:#9a3f1d;--pfg:#fff3de;--pacc:#ffd48a;--pline:rgba(255,243,222,.35);--nbg:#9a3f1d;--nfg:#fff3de;--nacc:#ffd48a;--jc:#9a3f1d;--hd:#9a3f1d;--fbg:#6e2a12;--ffg:#fff3de;--chgfg:#fff;--cface:#fff6e3;--crim:#b8651b;--ctick:#9a3f1d;--cnum:#3a2412;--chh:#3a2412;--cmh:#9a3f1d;--csh:#b8651b}
html[data-theme=rose]{--bg:#fbeff2;--paper:#fff8fa;--ink:#32151f;--mut:#80566a;--green:#7a2650;--brass:#b0507a;--sand:#ecc9d6;--tint:#f6dbe5;--pbg:#7a2650;--pfg:#fff4f8;--pacc:#ffc7dc;--pline:rgba(255,244,248,.35);--nbg:#7a2650;--nfg:#fff4f8;--nacc:#ffc7dc;--jc:#7a2650;--hd:#7a2650;--fbg:#561a39;--ffg:#fff4f8;--chgfg:#fff;--cface:#fff8fa;--crim:#b0507a;--ctick:#7a2650;--cnum:#32151f;--chh:#32151f;--cmh:#7a2650;--csh:#b0507a;--pat:none}
html[data-theme=ocean]{--bg:#e7f3f6;--paper:#f6fbfc;--ink:#0d2b36;--mut:#4b6c78;--green:#0b5a73;--brass:#0e7c8f;--sand:#bcdbe3;--tint:#d3eaf0;--pbg:#0b5a73;--pfg:#f2fbfd;--pacc:#8fe0ee;--pline:rgba(242,251,253,.35);--nbg:#0b5a73;--nfg:#f2fbfd;--nacc:#8fe0ee;--jc:#0b5a73;--hd:#0b5a73;--fbg:#083f51;--ffg:#f2fbfd;--chgfg:#fff;--cface:#f6fbfc;--crim:#0e7c8f;--ctick:#0b5a73;--cnum:#0d2b36;--chh:#0d2b36;--cmh:#0b5a73;--csh:#0e7c8f}
html[data-theme=contrast]{--bg:#000;--paper:#000;--ink:#fff;--mut:#d8d8d8;--green:#ffe600;--brass:#ffe600;--sand:#555;--tint:#262626;--pbg:#000;--pfg:#fff;--pacc:#ffe600;--pline:#888;--nbg:#ffe600;--nfg:#000;--nacc:#000;--jc:#ffe600;--hd:#ffe600;--fbg:#ffe600;--ffg:#000;--chgfg:#000;--cface:#000;--crim:#ffe600;--ctick:#fff;--cnum:#fff;--chh:#fff;--cmh:#ffe600;--csh:#fff;--pat:none}
</style>'''

ARRANGE_JS = r'''
function arrange(){var m=document.querySelector(".main"),el={dates:m.querySelector(".dates"),table:m.querySelector("table"),jum:m.querySelector(".jum"),chg:$("chg"),slide:$("slide")},
 lay=document.documentElement.getAttribute("data-layout"),two=/^(top|wide|wideright)$/.test(lay)&&matchMedia("(orientation:landscape)").matches,rows=[];
 SEC.forEach(function(k){el[k].classList.toggle("off",S.hide.indexOf(k)>=0)});
 var ord=S.order.filter(function(k){return S.hide.indexOf(k)<0});
 if(two){var right=ord.filter(function(k){return k!=="dates"&&k!=="table"});rows.push("auto");
  el.dates.style.gridColumn="1 / 3";el.dates.style.gridRow="1";el.table.style.gridColumn="1";el.table.style.gridRow="2 / -1";
  right.forEach(function(k,i){el[k].style.gridColumn="2";el[k].style.gridRow=String(i+2);rows.push(k==="slide"?"minmax(0,1fr)":"auto")})}
 else ord.forEach(function(k,i){el[k].style.gridColumn="1";el[k].style.gridRow=String(i+1);rows.push(k==="slide"?"minmax(0,1fr)":"auto")});
 m.style.gridTemplateRows=rows.join(" ")}
window.addEventListener("resize",function(){arrange()});
'''

def patch_index(s):
    s = rep(s, 'family=Amiri:wght@400;700&display=swap', 'family=Amiri:wght@400;700&family=Noto+Naskh+Arabic:wght@500;700&display=swap')
    s = rep(s, '.ar{font-family:Amiri,"Noto Naskh Arabic","Traditional Arabic",serif;direction:rtl}',
            '.ar{font-family:"Noto Naskh Arabic",Amiri,"Traditional Arabic",serif;direction:rtl;font-weight:500;letter-spacing:0;unicode-bidi:isolate}')
    s = rep(s, '/* ===== layouts ===== */', ARABIC_CSS)
    s = rep(s, '</style>', NEW_CSS)
    s = rep(s, 'images:[],timetable:{}};', 'images:[],timetable:{},order:["dates","table","jum","chg","slide"],hide:[]};')
    s = rep(s, 'var P=[["fajr"', 'var SEC=["dates","table","jum","chg","slide"];\nvar P=[["fajr"')
    s = rep(s, 'var THEMES=["classic","glass","liquid","simple","ramadan","mawlid","eid"],LAYS=["left","right","top","focus"]',
            'var THEMES=["classic","glass","liquid","simple","ramadan","mawlid","eid","midnight","desert","rose","ocean","contrast"],LAYS=["left","right","top","focus","bottom","wide","wideright"]')
    s = rep(s, 'if(typeof o.ticker==="string")r.ticker=o.ticker;',
            'if(typeof o.ticker==="string")r.ticker=o.ticker;\n'
            ' if(Array.isArray(o.order)){var q=o.order.filter(function(k,i){return SEC.indexOf(k)>=0&&o.order.indexOf(k)===i});SEC.forEach(function(k){if(q.indexOf(k)<0)q.push(k)});r.order=q}\n'
            ' if(Array.isArray(o.hide))r.hide=o.hide.filter(function(k){return SEC.indexOf(k)>=0});')
    s = rep(s, 'function load(o){S=merge(o);curKey="";si=0;look();tick()}', 'function load(o){S=merge(o);curKey="";si=0;look();arrange();tick()}')
    s = rep(s, 'function dkey(d){', ARRANGE_JS + 'function dkey(d){')
    s = rep(s, 'look();tick();setInterval(tick,1000);show();', 'look();arrange();tick();setInterval(tick,1000);show();')
    return s

ORDER_HTML = '''<section><h2>Screen sections</h2><p class="hint">Use the arrows to move sections up or down, and untick any you want to hide. In the “top” and “wide” layouts the date stays at the top and the prayer table on the left; the order applies to the other sections.</p><div id="ord"></div></section>

<section><h2>Default times'''

ORD_JS = r'''
var SECN={dates:"Date and Hijri date",table:"Prayer times table",jum:"Jumu’ah time",chg:"Jamat changes tomorrow notice",slide:"Rotating slides and announcements"};
function fixOrd(){var o=(S.order||[]).filter(function(x){return SECN[x]});Object.keys(SECN).forEach(function(x){if(o.indexOf(x)<0)o.push(x)});S.order=o;S.hide=(S.hide||[]).filter(function(x){return SECN[x]})}
function ords(){var b=$("ord");b.innerHTML="";S.order.forEach(function(k,i){var r=document.createElement("div");r.className="img";
 var g=document.createElement("div");g.className="grow";g.textContent=SECN[k];r.appendChild(g);
 var l=document.createElement("label"),c=document.createElement("input");l.className="c";c.type="checkbox";c.checked=S.hide.indexOf(k)<0;
 c.onchange=function(){var j=S.hide.indexOf(k);if(c.checked&&j>=0)S.hide.splice(j,1);if(!c.checked&&j<0)S.hide.push(k)};
 l.appendChild(c);l.appendChild(document.createTextNode("Show"));r.appendChild(l);
 [["▲",-1],["▼",1]].forEach(function(a){var bt=document.createElement("button");bt.className="s";bt.textContent=a[0];bt.setAttribute("aria-label",a[1]<0?"Move up":"Move down");
  bt.disabled=i+a[1]<0||i+a[1]>=S.order.length;bt.onclick=function(){var j=i+a[1],t=S.order[i];S.order[i]=S.order[j];S.order[j]=t;ords()};r.appendChild(bt)});
 b.appendChild(r)})}
'''

def patch_admin(s):
    s = rep(s, '["eid","Eid","linear-gradient(135deg,#0a7a5a,#ffd45a 60%,#ff8fb1)"]];',
            '["eid","Eid","linear-gradient(135deg,#0a7a5a,#ffd45a 60%,#ff8fb1)"],'
            '["midnight","Midnight","linear-gradient(135deg,#0a0f1f 55%,#e3b95b)"],'
            '["desert","Desert","linear-gradient(135deg,#9a3f1d 50%,#f4e4c8 50%)"],'
            '["rose","Rose","linear-gradient(135deg,#7a2650 50%,#fbeff2 50%)"],'
            '["ocean","Ocean","linear-gradient(135deg,#0b5a73 50%,#e7f3f6 50%)"],'
            '["contrast","High contrast","linear-gradient(135deg,#000 50%,#ffe600 50%)"]];')
    s = rep(s, '["focus","Big countdown, no analog clock","grid-template-columns:30% 1fr","b"]];',
            '["focus","Big countdown, no analog clock","grid-template-columns:30% 1fr","b"],'
            '["bottom","Clock bar at the bottom","grid-template-rows:1fr 30%","t"],'
            '["wide","Panel left, table and slides side by side","grid-template-columns:30% 1fr","b"],'
            '["wideright","Panel right, table and slides side by side","grid-template-columns:1fr 30%","b"]];')
    s = rep(s, 'if(t[0]==="right"){', 'if(/^(right|bottom|wideright)$/.test(t[0])){')
    s = rep(s, '<section><h2>Default times', ORDER_HTML)
    s = rep(s, 'S.images=S.images||[];', 'S.images=S.images||[];fixOrd();')
    s = rep(s, 'function fld(g,p){', ORD_JS + 'function fld(g,p){')
    s = rep(s, ';imgs();tt()}', ';imgs();tt();ords()}')
    return s

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    for path, fn in ((sys.argv[1], patch_index), (sys.argv[2], patch_admin)):
        src = open(path, encoding="utf-8").read()
        out = fn(src)
        shutil.copy(path, path + ".bak")
        open(path, "w", encoding="utf-8").write(out)
        print("Updated", path)