#!/usr/bin/env python3
"""Build ClipMap province shards and a lightweight 3,321-ward index.
Requires: pip install shapely (recommended for spatial fallback).
Usage:
 python tools/build_r2.py --provinces "Việt Nam (tỉnh thành) - 34.geojson" --wards VietnamWardBoundary2025.geojson --out dist-r2
 python tools/build_r2.py ... --out dist-r2 --allow-count-mismatch
 Upload *contents* of dist-r2/ to the root of the R2 bucket 'ranhgioi'.
"""
import argparse, collections, json, pathlib, re, sys, unicodedata
P_NAME=['ten_tinh','Ten_Tinh','TEN_TINH','tinh','province','province_name','NAME_1','TENTINH','tenTinh','ten_tinh_thanh','name_1','name','Name','NAME','TEN','Ten','ten']
W_NAME=['ten_xa','Ten_Xa','TEN_XA','xa','phuong','commune','commune_name','NAME_2','TENXA','tenXa','name_2','name','Name','NAME','TEN','Ten','ten','ward_name','wardName','TenDVHC','ten_dvhc']
P_CODE=['ma_tinh','MATINH','maTinh','province_code','code_1','MaTinh','MA_TINH','MATP','ma_tp','provinceCode']
W_P_NAME=['ten_tinh','Ten_Tinh','TEN_TINH','tinh','province','province_name','NAME_1','TENTINH','tenTinh','ten_tinh_thanh','ten_tp']
W_P_CODE=P_CODE
W_CODE=['ma_xa','MA_XA','maxa','MaXa','code','CODE','ward_code','MaDVHC','ma_dvhc','id']
def val(p,keys):
 for k in keys:
  v=p.get(k)
  if v is not None and str(v).strip(): return str(v).strip()
 return ''
def norm(s):
 return re.sub(r'\s+',' ',''.join(x for x in unicodedata.normalize('NFD',str(s).lower()) if not unicodedata.combining(x))).strip()
def read(path):
 with open(path,encoding='utf-8-sig') as f: obj=json.load(f)
 if obj.get('type')!='FeatureCollection': raise ValueError('Expected GeoJSON FeatureCollection: '+str(path))
 return [x for x in obj['features'] if x.get('geometry',{}).get('type') in ('Polygon','MultiPolygon')]
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--provinces',required=True);ap.add_argument('--wards',required=True);ap.add_argument('--out',default='dist-r2');ap.add_argument('--allow-count-mismatch',action='store_true')
 args=ap.parse_args()
 pfs=read(args.provinces); wfs=read(args.wards)
 print('Read',len(pfs),'province polygons and',len(wfs),'ward polygons',flush=True)
 if len(pfs)!=34 and not args.allow_count_mismatch: raise ValueError('Expected 34 province features; found '+str(len(pfs)))
 provinces=[];seen=set()
 for i,f in enumerate(pfs):
  props=f.get('properties') or {};name=val(props,P_NAME);code=val(props,P_CODE)
  if not name: raise ValueError('Province feature '+str(i)+' lacks recognizable name field: '+repr(list(props)[:30]))
  pid=code or str(i+1).zfill(2)
  if pid in seen: raise ValueError('Duplicate province code '+pid)
  seen.add(pid);provinces.append({'id':pid,'name':name,'code':code,'path':'provinces/'+pid+'.geojson','feature':f})
 by_code={norm(p['code']):p for p in provinces if p['code']}
 by_name={norm(p['name']):p for p in provinces}
 unmatched=[]; grouped=collections.defaultdict(list); wards_index=[]
 # Shapely only required when source ward attributes do not identify province.
 try:
  from shapely.geometry import shape
  from shapely.prepared import prep
  spatial=[(p,prep(shape(p['feature']['geometry']))) for p in provinces]
 except ImportError: spatial=[]
 for i,f in enumerate(wfs):
  props=f.get('properties') or {}
  p=by_code.get(norm(val(props,W_P_CODE))) or by_name.get(norm(val(props,W_P_NAME)))
  if p is None and spatial:
   from shapely.geometry import shape
   point=shape(f['geometry']).representative_point()
   p=next((p for p,geom in spatial if geom.intersects(point)),None)
  if p is None:
   unmatched.append({'row':i,'ward':val(props,W_NAME),'province':val(props,W_P_NAME)})
   continue
  name=val(props,W_NAME);wid=val(props,W_CODE) or str(i+1)
  if not name: raise ValueError('Ward lacks recognizable name, row '+str(i)+' fields '+repr(list(props)[:20]))
  grouped[p['id']].append(f);wards_index.append({'id':wid,'name':name,'provinceId':p['id']})
 if unmatched:
  out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
  (out/'unmatched.json').write_text(json.dumps(unmatched,ensure_ascii=False,indent=2),encoding='utf-8')
  raise ValueError(str(len(unmatched))+' ward(s) could not be matched. Inspect '+str(out/'unmatched.json')+'; no dataset emitted.')
 if len(wards_index)!=3321 and not args.allow_count_mismatch: raise ValueError('Expected 3,321 wards, got '+str(len(wards_index))+'. Use --allow-count-mismatch only after auditing source.')
 out=pathlib.Path(args.out);(out/'provinces').mkdir(parents=True,exist_ok=True)
 for p in provinces:
  f=p.pop('feature');features=grouped[p['id']]
  dest=out/p['path']
  dest.write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
  p['wardCount']=len(features)
 # tiny overview polygons may still be sourced from original province GeoJSON separately.
 (out/'index.json').write_text(json.dumps({'schema':'clipmap-r2-index-v1','crs':'EPSG:4326','provinces':provinces,'wards':wards_index},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('SUCCESS: index.json and',len(provinces),'province shards,',len(wards_index),'ward entries')
 print('Upload contents of',out,'to R2 (not the parent folder).',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERROR:',e,file=sys.stderr);sys.exit(1)
