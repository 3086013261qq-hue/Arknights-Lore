from pathlib import Path
import argparse, json, re, csv

FIELD_PATTERNS = {
    'visual_weapon': re.compile(r'^-?\s*可见武器装备\s*:\s*(.*)$', re.M),
    'combat_weapon': re.compile(r'^武器/战斗方式\s*:\s*(.*)$', re.M),
    'role': re.compile(r'^定位\s*:\s*(.*)$', re.M),
    'species': re.compile(r'^种族\s*:\s*(.*)$', re.M),
    'identity': re.compile(r'^身份\s*:\s*(.*)$', re.M),
}

VAGUE = ('职业定位','稳定单体法术','高强度近战','以法术','以源石技艺','远程攻击','近战攻击','根据职业','以技能','常规攻击','战术定位','当前形态')
MEDIA_WORDS = ('法杖','施术单元','源石技艺媒介','源石单元','终端','装置','无人机','乐器','医疗设备')


def field(text, pat):
    m = pat.search(text)
    return m.group(1).strip() if m else ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='build/weapon-audit')
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    rows=[]
    for category, folder in [('operator', Path('worldbook/operators')), ('npc', Path('worldbook/npcs'))]:
        if not folder.exists():
            continue
        for p in sorted(folder.glob('*.md'), key=lambda x:x.name.casefold()):
            text=p.read_text(encoding='utf-8')
            visual=field(text, FIELD_PATTERNS['visual_weapon'])
            combat=field(text, FIELD_PATTERNS['combat_weapon'])
            role=field(text, FIELD_PATTERNS['role'])
            species=field(text, FIELD_PATTERNS['species'])
            identity=field(text, FIELD_PATTERNS['identity'])
            all_weapon_lines=[ln.strip() for ln in text.splitlines() if ('武器' in ln or '铳' in ln or '剑' in ln or '刀' in ln or '弓' in ln or '弩' in ln or '枪' in ln or '盾' in ln or '法杖' in ln)][:12]
            flags=[]
            if not combat: flags.append('missing_combat_weapon')
            if not visual: flags.append('missing_visual_weapon')
            if combat and any(v in combat for v in VAGUE): flags.append('combat_too_generic')
            if visual and combat and visual != combat:
                # Differences are normal, but mark only stronger contradictions.
                none_words=('无明显武器','未见明显武器','无固定武器','不使用常规武器')
                if any(x in visual for x in none_words) and not any(x in combat for x in none_words):
                    flags.append('visual_vs_combat_possible_conflict')
            if any(w in combat for w in MEDIA_WORDS) and ('武器' not in combat and '攻击' not in combat and '战斗' not in combat):
                flags.append('possible_medium_as_weapon')
            if '具体制式未公开' in combat or '不作推定' in combat: flags.append('conservative_unresolved')
            rows.append({
                'category':category,'name':p.stem,'path':str(p),'species':species,'identity':identity,'role':role,
                'visual_weapon':visual,'combat_weapon':combat,'flags':flags,'weapon_context':all_weapon_lines
            })
    summary={
        'total':len(rows),
        'operators':sum(r['category']=='operator' for r in rows),
        'npcs':sum(r['category']=='npc' for r in rows),
        'missing_combat_weapon':sum('missing_combat_weapon' in r['flags'] for r in rows),
        'missing_visual_weapon':sum('missing_visual_weapon' in r['flags'] for r in rows),
        'combat_too_generic':sum('combat_too_generic' in r['flags'] for r in rows),
        'possible_conflicts':sum('visual_vs_combat_possible_conflict' in r['flags'] for r in rows),
        'possible_medium_as_weapon':sum('possible_medium_as_weapon' in r['flags'] for r in rows),
        'conservative_unresolved':sum('conservative_unresolved' in r['flags'] for r in rows),
    }
    (out/'weapon-audit.json').write_text(json.dumps({'summary':summary,'rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'weapon-audit.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t')
        w.writerow(['category','name','species','role','visual_weapon','combat_weapon','flags','weapon_context'])
        for r in rows:
            w.writerow([r['category'],r['name'],r['species'],r['role'],r['visual_weapon'],r['combat_weapon'],','.join(r['flags']),' || '.join(r['weapon_context'])])
    flagged=[r for r in rows if r['flags']]
    md=['# 481-character weapon audit extraction','',f"- total: {summary['total']}",f"- operators: {summary['operators']}",f"- npcs: {summary['npcs']}",f"- missing combat weapon: {summary['missing_combat_weapon']}",f"- missing visual weapon: {summary['missing_visual_weapon']}",f"- generic combat descriptions: {summary['combat_too_generic']}",f"- possible visual/combat conflicts: {summary['possible_conflicts']}",f"- possible medium-as-weapon: {summary['possible_medium_as_weapon']}",f"- conservative unresolved: {summary['conservative_unresolved']}",'','## Flagged']
    for r in flagged:
        md += ['', f"### {r['category']} / {r['name']}", f"- flags: {', '.join(r['flags'])}", f"- visual: {r['visual_weapon'] or '(missing)'}", f"- combat: {r['combat_weapon'] or '(missing)'}"]
    (out/'SUMMARY.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))

if __name__=='__main__':
    main()
