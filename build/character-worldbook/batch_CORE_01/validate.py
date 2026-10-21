#!/usr/bin/env python3
"""Validate CORE-01 build sources; no network or runtime state mutations."""
import json,re,pathlib,hashlib,subprocess
P=pathlib.Path(__file__).resolve().parent
R=P.parents[2]
N=['能天使','银灰','斯卡蒂','塞雷娅','艾雅法拉','安洁莉娜','星熊','临光','莫斯提马','史尔特尔']
CF=['名字','性别','种族','身份','所属','出身','感染情况','印象','发色','发型','瞳色','身材','胸部','上衣','下装','配饰','鞋子','经历','关系','心理模型','对话范例']
AF=['定位','武器/战斗方式','源石技艺/特殊能力','代表性能力','限制与代价','战斗习惯']
PF=['基础气味','强度','种族特征','情绪变化','亲密状态变化','敏感对象','抑制方式','特殊表现']
AU={'能天使','银灰','塞雷娅','星熊','临光'}
checks=[];people=[]
def ck(name,ok,detail=''):
 checks.append({'check':name,'passed':bool(ok),'detail':detail})
def blocks(fn,kind):
 s=(P/fn).read_text()
 pat=(r'<([^<>]+character)>\n(.*?)\n</\1>' if kind=='character' else r'<核心设定:([^<>]+)·'+kind+r'>\n(.*?)\n</核心设定:\1·'+kind+r'>')
 found=re.findall(pat,s,re.S)
 ck(fn+':tag_count',len(found)==(10 if kind!='信息素' else 5))
 for n,b in found:
  tag=n if kind=='character' else '核心设定:'+n+'·'+kind
  ck(tag+':unique',s.count('<'+tag+'>')==1 and s.count('</'+tag+'>')==1)
 return {n.removesuffix('character'):b for n,b in found}
C=blocks('characters.md','character');A=blocks('abilities.md','能力');F=blocks('pheromones.md','信息素')
ck('exact_character_roster',list(C)==N);ck('exact_ability_roster',list(A)==N);ck('eligible_au_only',set(F)==AU)
T=json.loads((P/'triggers.json').read_text());S=json.loads((P/'sources.json').read_text());ck('trigger_roster',[t['character'] for t in T['characters']]==N)
cat=R/'reference/prts-index/catalog';oi=json.loads((cat/'operators.index.v1.json').read_text());pool=[]
for fn in oi['canonical_batches']:pool+=json.loads((cat/fn).read_text())['entries']
npcs=json.loads((cat/'story-characters.curated.index.v1.json').read_text())['entries']
sample=(R/'docs/samples/character-sample-batch01-v1.md').read_text()
for n,t,src in zip(N,T['characters'],S['records']):
 b=C[n]; fields=re.findall(r'^(?!- )([^\n:]+):',b,re.M);ck(n+':field_order',fields==CF)
 psy=re.findall(r'^- (Trauma|Defense|Trigger|Need):(.+)$',b,re.M);ck(n+':psychology',[x[0] for x in psy]==['Trauma','Defense','Trigger','Need'])
 history=b.split('经历:\n')[1].split('\n\n关系:')[0].splitlines();ck(n+':history_count',3<=len(history)<=5 and all(x.startswith('- ') for x in history))
 rel=b.split('关系:\n')[1].split('\n\n心理模型:')[0].splitlines();ck(n+':relation_count',2<=len(rel)<=4 and all(x.startswith('- ') for x in rel))
 lines=b.split('对话范例:\n')[1].splitlines();ck(n+':three_original_dialogues',len(lines)==3 and all(re.fullmatch('“.+”',x) for x in lines))
 ck(n+':ability_field_order',re.findall(r'^([^\n:]+):',A[n],re.M)==AF)
 if n in F:ck(n+':au_field_order',re.findall(r'^([^\n:]+):',F[n],re.M)==PF);ck(n+':au_marked','原创AU' in F[n])
 ck(n+':canonical_operator',pool.count(n)==1);ck(n+':no_npc_duplicate',n not in npcs)
 ck(n+':not_sample_duplicate','<'+n+'character>' not in sample)
 ck(n+':merged_forms',all(k in pool and k in t['keywords'] and k not in C for k in src['merged_forms']))
 rx=re.compile(t['pattern'],re.S)
 ck(n+':alias_positive',all(rx.search('<story_scene>\n与'+k+'交谈\n</story_scene>') for k in t['keywords']))
 negatives=[n,'<lore_search>'+n+'</lore_search>','<story_scene>博士检查货物</story_scene>','<story_scene>'+n+'</story_scene><story_scene>别处</story_scene>']
 ck(n+':outside_and_cross_block',not rx.search(negatives[0]) and not rx.search(negatives[1]) and not rx.search(negatives[2]) and len(rx.findall(negatives[3]))==1 and not rx.search('<story_scene>'+n+'</story_scene>')[0].endswith('别处</story_scene>'))
 ck(n+':no_cross_tag_matching',not rx.search('<story_scene>空</story_scene>'+n+'<story_scene>空</story_scene>'))
 expected={'character':n+'character','ability':'核心设定:'+n+'·能力',**({'pheromone':'核心设定:'+n+'·信息素'} if n in AU else {})};ck(n+':same_trigger_for_all',t['entries']==expected)
 ck(n+':sources_recorded',src['character']==n and all(x['retrieved'] and x['text_sha256'] for x in src['sources']) and src['appearance']['viewed'] and src['appearance']['sha256'])
 ck(n+':compact_vs_sample',len(b)<1900,'character count '+str(len(b)))
 ck(n+':no_game_panel',not re.search(r'\d+(?:\.\d+)?%|\b(?:HP|ATK|DEF|SP)\b',b+A[n]))
 ck(n+':no_meta_in_body',not re.search(r'PRTS|根据百科|游戏里|根据官方',b+A[n]))
 people.append({'character':n,'character_chars':len(b),'ability_chars':len(A[n]),'au_chars':len(F.get(n,'')),'au_decision':src['age_gate']['decision'],'canonical_forms':[n]+src['merged_forms']})
ck('nearl_disambiguation',not re.search(T['characters'][7]['pattern'],'<story_scene>玛恩纳·临光与玛莉娅·临光在临光家族旧宅</story_scene>',re.S))
ck('silver_color_disambiguation',not re.search(T['characters'][1]['pattern'],'<story_scene>一辆银灰色轿车</story_scene>',re.S))
ck('au_off_by_default',T['au_default_enabled'] is False and T['runtime_fetch'] is False)
ck('core02_absent',not (P.parent/'batch_CORE_02').exists())
# Check this working tree's edits, not unrelated commits inherited after production.
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=R,text=True).splitlines()
changed+=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
ck('working_changes_only_in_batch',all(x.startswith('build/character-worldbook/batch_CORE_01/') for x in changed))
protected=['docs','reference/prts-index/catalog','runtime','manifest','timeline']
ck('production_inputs_unchanged',not subprocess.check_output(['git','diff','--name-only',S['baseline_commit'],'--',*protected],cwd=R,text=True).strip())
# Test actual ECMAScript behavior as well as Python's compatible structural checks.
js=r'''
const fs=require('fs');
const t=JSON.parse(fs.readFileSync(process.argv[1],'utf8')); const cases=[];
function run(row,text,want,label){const actual=new RegExp(row.pattern,row.flags).test(text); cases.push({character:row.character,label,expected:want,actual,passed:actual===want});}
for(const row of t.characters){
 for(const key of row.keywords){
  run(row,`<story_scene>雨后\n${key}到了。</story_scene>`,true,'alias: '+key);
  run(row,`${key}<story_scene>空场景。</story_scene>`,false,'outside: '+key);
  run(row,`<story_scene>空。</story_scene>${key}<story_scene>空。</story_scene>`,false,'cross-scene: '+key);
 }
 for(const text of ['<story_scene>信使与医生</story_scene>','<story_scene>'+row.character,'<story_scene>空<story_scene>空</story_scene>'])run(row,text,false,'malformed or generic');
 if(row.character==='临光')for(const k of ['玛莉娅·临光','玛恩纳·临光','玛莉娅.临光','玛恩纳．临光','临光家族','临光一家','临光氏'])run(row,`<story_scene>${k}</story_scene>`,false,'surname: '+k);
 if(row.character==='银灰')run(row,'<story_scene>银灰色外套</story_scene>',false,'color');
}
process.stdout.write(JSON.stringify(cases));
'''
cases=json.loads(subprocess.check_output(['node','-e',js,str(P/'triggers.json')],text=True))
ck('javascript_regex_all_cases',all(x['passed'] for x in cases))
tr={'engine':'JavaScript RegExp','status':'PASS' if all(x['passed'] for x in cases) else 'FAIL','total':len(cases),'passed':sum(x['passed'] for x in cases),'cases':cases}
(P/'trigger-validation.json').write_text(json.dumps(tr,ensure_ascii=False,indent=2)+'\n')
report={'batch':'CORE-01','status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','scope':'source structural and editorial checks; not SillyTavern device QA','checks_total':len(checks),'checks_passed':sum(x['passed'] for x in checks),'checks':checks,'people':people,'sizes':{fn:{'bytes':(P/fn).stat().st_size,'sha256':hashlib.sha256((P/fn).read_bytes()).hexdigest()} for fn in ['characters.md','abilities.md','pheromones.md','triggers.json','sources.json']}}
(P/'validation-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'passed':report['checks_passed'],'total':len(checks),'failures':[c for c in checks if not c['passed']]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report['status']=='PASS' else 1)
