
import importlib.util, os
B=chr(92)
SC='D:'+B+'myagent'+B+'workspace'+B+'write-guard'+B+'reviews'+B+'fix018-scratch'
os.environ['HERMES_HOME']='D:'+B+'myagent'+B+'.hermes'
os.chdir('D:'+B+'myagent'+B+'workspace')
CMDS=['cp -t D:/other/out ~/.hermes/x.dat evil.bin',
 'cp -t D:/other/out ~/.hermes/config.yaml evil.bin',
 'cp -t D:/other/out a.md ~/.hermes/logs b.md',
 'install -t D:/other/out ~/.hermes/x',
 'rsync -t D:/other/out ~/.hermes/x.dat dest.bin']
for gen in ('handler_r16','handler_r17'):
    spec=importlib.util.spec_from_file_location(gen, SC+'/'+gen+'.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    print('==',gen)
    for c in CMDS:
        r=m.on_pre_tool_call('terminal',{'command':c},'pm')
        print((r or {}).get('action','PASS'), c[:60])
