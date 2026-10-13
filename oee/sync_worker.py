#!/usr/bin/env python3
"""OEE Cantos | sincronizador interno, sin paquetes adicionales.
Instalar junto a agente_cantos.py + inteq_real.py de la V3; credenciales solo en .env privado.
NO usar sin validar primero contador cinchos, metas, zona horaria y credenciales de TI.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from zoneinfo import ZoneInfo
from agente_cantos import load_env, read_config, query_all, render_report

BASE=Path(__file__).resolve().parent
URL="https://ezhlltgcqektrclgzhfi.supabase.co"

def send_rows(rows, start, validated):
    key=os.environ.get("SUPABASE_SERVICE_ROLE_KEY","").strip()
    if not key: raise RuntimeError("Falta SUPABASE_SERVICE_ROLE_KEY; no colocarla en GitHub")
    if not validated: raise RuntimeError("Contador cinchos no validado; no se permite enviar datos de producción")
    payload=[]
    for r in rows:
        quality="parcial" if r.get("parcial") else ("validado" if r.get("produccion") is not None else "sin_datos")
        payload.append({
            "machine":r["maquina"],"slot":start.isoformat(),
            "units":r.get("produccion") if quality=="validado" else None,
            "target_units":r.get("meta"),
            "efficiency_pct":r.get("eficiencia") if quality=="validado" else None,
            "occupancy_pct":r.get("ocupacion"),
            "idle_minutes":r.get("minutos_paro"),
            "state":r.get("estado","SIN DATOS"),"quality":quality,
            "samples":r.get("muestras",0),"reset_count":r.get("reinicios",0),
            "notes":"; ".join(r.get("warnings",[]))[:1800],
        })
    req=urllib.request.Request(
        URL+"/rest/v1/oc_machine_hourly?on_conflict=machine%2Cslot",
        data=json.dumps(payload,ensure_ascii=False).encode(),
        headers={"apikey":key,"Authorization":"Bearer "+key,
                 "Content-Type":"application/json","Prefer":"resolution=merge-duplicates"},
        method="POST")
    with urllib.request.urlopen(req,timeout=35) as res:
        if not 200<=res.status<300: raise RuntimeError("Falló ingesta: HTTP "+str(res.status))
    return len(payload)

def main():
    load_env()
    cfg=read_config()
    if not cfg.get("contador_validado"):
        raise RuntimeError("Antes valida el contador cinchos en planta y activa contador_validado en config.json")
    tz=ZoneInfo("America/Guatemala")
    end=dt.datetime.now(tz).replace(minute=0,second=0,microsecond=0)
    start=end-dt.timedelta(hours=1)
    rows=query_all(cfg,start,end)
    title,body=render_report(cfg,start,end,rows)
    print(body)
    if "--send" not in sys.argv:
        print("\nMODO SEGURO: no se subió nada. Usa --send solo después de revisar resultados.")
        return
    if any(r.get("parcial") for r in rows):
        print("\nAVISO: Existen lecturas parciales; no se publicarán unidades sin validación.")
    count=send_rows(rows,start,cfg["contador_validado"])
    print("Guardadas",count,"filas en Supabase para",start.isoformat())
    print("Teams/Outlook: aún no se envía; integrar flujo después de validar la ingesta.")

if __name__=="__main__":
    try: main()
    except (Exception) as ex:
        # No imprimir tokens ni URLs privadas accidentalmente.
        print("ERROR de sincronización:",str(ex).split("Bearer ")[0][:240],file=sys.stderr)
        sys.exit(1)
