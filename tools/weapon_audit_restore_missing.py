from pathlib import Path
import subprocess, shutil, json

MISSING_BY_COMMIT = {
    '6c0255999b9663f787b1620caa029227d53bd7e2': [
        '初雪','刺玫','刻俄柏','刻刀','医生','华法琳','协律','卡夫卡','卡涅利安','卡缇'
    ],
    '31be582a9695a8b5bdaabc250862af007ac7a93e': [
        '梅','梅尔','梓兰','棘刺','森蚺','森西','槐琥','歌蕾蒂娅','止颂','正义骑士号'
    ],
    '3a97bc39a018a184a52f27e9acd92e4fd3149920': [
        '琴柳','瑕光','瑰盐','电弧','白金','白铁','白雪','白面鸮','百炼嘉维尔','盟约·辅助干员'
    ],
    '351ab4a9440338431fd3ea71d46c932fddecd3fb': [
        '罗小黑','罗德岛隐秘队','罗比菈塔','羽毛笔','翎羽','耀骑士临光','老鲤','耶拉','聆音','能天使'
    ],
}

out_root = Path('build/weapon-audit/restored')
out_root.mkdir(parents=True, exist_ok=True)
records=[]
for commit, names in MISSING_BY_COMMIT.items():
    for name in names:
        path = f'worldbook/operators/{name}.md'
        target = Path(path)
        existed = target.exists()
        if not existed:
            content = subprocess.check_output(['git','show',f'{commit}:{path}'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        shutil.copy2(target, out_root / f'{name}.md')
        records.append({'name':name,'path':path,'source_commit':commit,'was_missing':not existed})
Path('build/weapon-audit/restored-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'restored':sum(r['was_missing'] for r in records),'total_candidates':len(records)},ensure_ascii=False))
