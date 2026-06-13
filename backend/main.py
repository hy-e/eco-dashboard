from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
import random, math, datetime

app = FastAPI(title="ECO Dashboard API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Constants ──────────────────────────────────────────────────────────────

PROCESSES = ["ETCH", "CVD", "PVD", "IMP", "PHOTO", "CMP", "DIFF"]
ECO_DESCS = [
    "Gate oxide thickness optimization", "Metal line width reduction",
    "Via hole etch recipe change", "Implant dose adjustment",
    "Chemical slurry change for CMP", "Photoresist thickness update",
    "Diffusion temperature profile change", "STI etch depth modification",
    "Barrier metal deposition change", "Contact resistance improvement",
]
STEP_SEQS = ["PRE", "IN-LINE", "POST", "FINAL"]

BASE_PARAMS = {
    "Yield_TOTAL": {"base": 95.0,   "sigma": 2.0,   "unit": "%"},
    "Yield_STEP1": {"base": 97.5,   "sigma": 1.5,   "unit": "%"},
    "Vt_NMOS":     {"base": 0.520,  "sigma": 0.012, "unit": "V"},
    "Vt_PMOS":     {"base": -0.510, "sigma": 0.013, "unit": "V"},
    "Idsat_NMOS":  {"base": 1.200,  "sigma": 0.050, "unit": "mA/um"},
    "Idsat_PMOS":  {"base": 0.800,  "sigma": 0.040, "unit": "mA/um"},
    "Ioff_NMOS":   {"base": 2.500,  "sigma": 0.400, "unit": "nA/um"},
    "Ioff_PMOS":   {"base": 1.800,  "sigma": 0.300, "unit": "nA/um"},
    "Rs_NPLUS":    {"base": 60.0,   "sigma": 2.0,   "unit": "Ω/sq"},
    "Rp_POLY":     {"base": 150.0,  "sigma": 5.0,   "unit": "Ω/sq"},
    "Cg_NMOS":     {"base": 12.0,   "sigma": 0.50,  "unit": "fF/um"},
    "Bin1":        {"base": 95.0,   "sigma": 1.5,   "unit": "%"},
    "Bin2":        {"base": 2.5,    "sigma": 0.5,   "unit": "%"},
}

CATEGORY_PARAMS = {
    "Yield":   ["Yield_TOTAL", "Yield_STEP1"],
    "Vt":      ["Vt_NMOS", "Vt_PMOS"],
    "Idsat":   ["Idsat_NMOS", "Idsat_PMOS"],
    "Leakage": ["Ioff_NMOS", "Ioff_PMOS"],
    "Rs":      ["Rs_NPLUS"],
    "Rp":      ["Rp_POLY"],
    "Cg":      ["Cg_NMOS"],
    "EDS Bin": ["Bin1", "Bin2"],
}

BASE_DATE = datetime.datetime(2024, 3, 1)

# ── Helpers ───────────────────────────────────────────────────────────────

def _r(v, d=4):
    return round(v, d)

def compute_stats(values):
    n = len(values)
    avg = sum(values) / n
    sv = sorted(values)
    med = sv[n // 2] if n % 2 else (sv[n // 2 - 1] + sv[n // 2]) / 2
    std = math.sqrt(sum((v - avg) ** 2 for v in values) / n)
    return {
        "avg": _r(avg), "med": _r(med), "std": _r(std),
        "q1":  _r(sv[n // 4]), "q3": _r(sv[3 * n // 4]),
        "min": _r(sv[0]), "max": _r(sv[-1]), "n": n,
    }

def get_eco_significant_params(eco_no):
    """Deterministic (HIGH/MEDIUM/LOW) params per ECO."""
    random.seed(hash(eco_no) % 100000)
    all_p = [p for ps in CATEGORY_PARAMS.values() for p in ps]
    n_hm = random.randint(2, 5)
    n_lo = random.randint(1, 3)
    shuffled = all_p[:]
    random.shuffle(shuffled)
    hm  = set(shuffled[:n_hm])
    low = set(shuffled[n_hm: n_hm + n_lo])
    return hm, low

def get_param_raw(eco_no, parameter, hm, low):
    """Reproducible ref/eco value lists + significance level."""
    info = BASE_PARAMS[parameter]
    base, sigma = info["base"], info["sigma"]
    random.seed(hash(eco_no + parameter) % 100000)

    if parameter in hm:
        shift = random.uniform(1.5, 3.0) * sigma * random.choice([-1, 1])
        sig   = random.choice(["HIGH", "MEDIUM"])
    elif parameter in low:
        shift = random.uniform(0.8, 1.5) * sigma * random.choice([-1, 1])
        sig   = "LOW"
    else:
        shift = random.uniform(-0.3, 0.3) * sigma
        sig   = "NONE"

    ref_n  = random.randint(20, 40)
    eco_n  = random.randint(10, 25)
    emult  = random.uniform(0.9, 1.3)
    ref_v  = [random.gauss(base,         sigma)        for _ in range(ref_n)]
    eco_v  = [random.gauss(base + shift, sigma * emult) for _ in range(eco_n)]
    return ref_v, eco_v, sig

def sig_metrics(ref_s, eco_s, sigma):
    m = []
    if abs(eco_s["avg"] - ref_s["avg"]) > 1.2 * sigma:              m.append("avg")
    if abs(eco_s["med"] - ref_s["med"]) > 1.2 * sigma:              m.append("med")
    if ref_s["std"] > 0 and not (0.77 < eco_s["std"] / ref_s["std"] < 1.3): m.append("std")
    if abs(eco_s["q1"]  - ref_s["q1"])  > 1.5 * sigma:              m.append("q1")
    if abs(eco_s["q3"]  - ref_s["q3"])  > 1.5 * sigma:              m.append("q3")
    return m

def make_timestamps(n, days_start, days_end, seed):
    random.seed(seed)
    ts = []
    for _ in range(n):
        d = random.uniform(days_start, days_end)
        h = random.uniform(0, 24)
        dt = BASE_DATE - datetime.timedelta(days=d, hours=h)
        ts.append(dt.strftime("%Y-%m-%dT%H:%M:%S"))
    return sorted(ts)

# ── ECO List ──────────────────────────────────────────────────────────────

random.seed(42)

def _make_ecos():
    ecos = []
    for i in range(1, 31):
        eco_no = f"ECO-2024-{i:04d}"
        ecos.append({
            "eco_no": eco_no,
            "process_id": random.choice(PROCESSES),
            "eco_desc":   random.choice(ECO_DESCS),
            "lot_count":  random.randint(5, 50),
            "eds_lot_count": 0,
            "step_seq":   random.choice(STEP_SEQS),
            "status":     "DONE" if i <= 18 else "IN-PROGRESS",
        })
    # fix eds_lot_count after lot_count is set
    random.seed(42)
    for e in ecos:
        random.choice(PROCESSES)  # consume same random stream
        random.choice(ECO_DESCS)
        lc = random.randint(5, 50)
        e["eds_lot_count"] = random.randint(3, lc)
        random.choice(STEP_SEQS)
    return ecos

ECO_LIST = _make_ecos()
ECO_MAP  = {e["eco_no"]: e for e in ECO_LIST}

# ── Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    total = len(ECO_LIST)
    done  = sum(1 for e in ECO_LIST if e["status"] == "DONE")
    return {"total_ecos": total, "done_ecos": done, "in_progress": total - done}

@app.get("/api/step-seqs")
def get_step_seqs():
    return STEP_SEQS

@app.get("/api/ecos")
def get_ecos(eco_no: Optional[str] = Query(None), step_seq: Optional[str] = Query(None)):
    result = ECO_LIST
    if eco_no:    result = [e for e in result if eco_no.upper() in e["eco_no"].upper()]
    if step_seq:  result = [e for e in result if e["step_seq"] == step_seq]
    done = sum(1 for e in result if e["status"] == "DONE")
    return {"total": len(result), "done_count": done, "items": result}

@app.get("/api/ecos/{eco_no}/summary")
def get_summary(eco_no: str):
    hm, low = get_eco_significant_params(eco_no)
    all_p = [p for ps in CATEGORY_PARAMS.values() for p in ps]
    total = len(all_p)
    detected = sum(1 for p in all_p if p in hm or p in low)
    items = []
    for cat, params in CATEGORY_PARAMS.items():
        random.seed(hash(eco_no + cat) % 10000)
        det = sum(1 for p in params if p in hm or p in low)
        items.append({
            "category": cat,
            "total": len(params), "detected": det,
            "change_rate": round(random.uniform(-5, 5), 2),
            "significance": "HIGH" if det == len(params) else ("MEDIUM" if det else "NONE"),
        })
    return {
        "eco_no": eco_no, "total_items": total, "detected_items": detected,
        "detection_rate": round(detected / total * 100, 1) if total else 0,
        "items": items,
    }

@app.get("/api/ecos/{eco_no}/analysis")
def get_analysis(eco_no: str):
    hm, low = get_eco_significant_params(eco_no)
    items = []
    sig_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}

    for cat, params in CATEGORY_PARAMS.items():
        for param in params:
            info = BASE_PARAMS[param]
            ref_v, eco_v, significance = get_param_raw(eco_no, param, hm, low)
            ref_s = compute_stats(ref_v)
            eco_s = compute_stats(eco_v)
            delta  = _r(eco_s["avg"] - ref_s["avg"])
            delta_pct = _r(delta / abs(ref_s["avg"]) * 100) if ref_s["avg"] else 0
            items.append({
                "parameter": param, "category": cat, "unit": info["unit"],
                "ref_stats": ref_s, "eco_stats": eco_s,
                "delta_avg": delta, "delta_pct": delta_pct,
                "sig_metrics": sig_metrics(ref_s, eco_s, info["sigma"]),
                "significance": significance,
            })

    items.sort(key=lambda x: sig_order[x["significance"]])
    detected = sum(1 for i in items if i["significance"] != "NONE")
    return {
        "eco_no": eco_no,
        "total_params": len(items), "detected_params": detected,
        "detection_rate": round(detected / len(items) * 100, 1) if items else 0,
        "items": items,
    }

@app.get("/api/ecos/{eco_no}/items/{parameter}/data")
def get_item_data(eco_no: str, parameter: str):
    if parameter not in BASE_PARAMS:
        raise HTTPException(404, f"Unknown parameter: {parameter}")
    hm, low = get_eco_significant_params(eco_no)
    ref_v, eco_v, significance = get_param_raw(eco_no, parameter, hm, low)
    info = BASE_PARAMS[parameter]

    seed = hash(eco_no + parameter + "ts") % 100000
    ref_ts  = make_timestamps(len(ref_v), 60, 31, seed)
    eco_ts  = make_timestamps(len(eco_v), 30,  1, seed + 1)

    ref_data = [{"time": t, "value": _r(v), "lot_id": f"REF-{i+1:03d}"}
                for i, (t, v) in enumerate(zip(ref_ts, ref_v))]
    eco_data = [{"time": t, "value": _r(v), "lot_id": f"ECO-{i+1:03d}"}
                for i, (t, v) in enumerate(zip(eco_ts, eco_v))]

    return {
        "eco_no": eco_no, "parameter": parameter, "unit": info["unit"],
        "ref_data": ref_data, "eco_data": eco_data,
        "ref_stats": compute_stats(ref_v), "eco_stats": compute_stats(eco_v),
        "significance": significance,
    }
