from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
import random

app = FastAPI(title="ECO Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mock Data ---

PROCESSES = ["ETCH", "CVD", "PVD", "IMP", "PHOTO", "CMP", "DIFF"]
ECO_DESCS = [
    "Gate oxide thickness optimization",
    "Metal line width reduction",
    "Via hole etch recipe change",
    "Implant dose adjustment",
    "Chemical slurry change for CMP",
    "Photoresist thickness update",
    "Diffusion temperature profile change",
    "STI etch depth modification",
    "Barrier metal deposition change",
    "Contact resistance improvement",
]

STEP_SEQS = ["PRE", "IN-LINE", "POST", "FINAL"]

random.seed(42)

def make_ecos():
    ecos = []
    for i in range(1, 31):
        eco_no = f"ECO-2024-{i:04d}"
        process_id = random.choice(PROCESSES)
        eco_desc = random.choice(ECO_DESCS)
        lot_count = random.randint(5, 50)
        eds_lot_count = random.randint(3, lot_count)
        step_seq = random.choice(STEP_SEQS)
        status = "DONE" if i <= 18 else "IN-PROGRESS"
        ecos.append({
            "eco_no": eco_no,
            "process_id": process_id,
            "eco_desc": eco_desc,
            "lot_count": lot_count,
            "eds_lot_count": eds_lot_count,
            "step_seq": step_seq,
            "status": status,
        })
    return ecos

ECO_LIST = make_ecos()

def make_summary(eco_no: str):
    random.seed(hash(eco_no) % 10000)
    total_items = random.randint(10, 50)
    detected_items = random.randint(0, total_items)

    items = []
    categories = ["Yield", "Vt", "Idsat", "Leakage", "Rs", "Rp", "Cg", "EDS Bin"]
    for cat in categories:
        item_count = random.randint(1, 6)
        det_count = random.randint(0, item_count)
        items.append({
            "category": cat,
            "total": item_count,
            "detected": det_count,
            "change_rate": round(random.uniform(-5.0, 5.0), 2),
            "significance": random.choice(["HIGH", "MEDIUM", "LOW", "NONE"]),
        })

    return {
        "eco_no": eco_no,
        "total_items": total_items,
        "detected_items": detected_items,
        "detection_rate": round(detected_items / total_items * 100, 1) if total_items else 0,
        "items": items,
    }


# --- Schemas ---

class EcoItem(BaseModel):
    eco_no: str
    process_id: str
    eco_desc: str
    lot_count: int
    eds_lot_count: int
    step_seq: str
    status: str

class EcoListResponse(BaseModel):
    total: int
    done_count: int
    items: List[EcoItem]

class SummaryItem(BaseModel):
    category: str
    total: int
    detected: int
    change_rate: float
    significance: str

class EcoSummary(BaseModel):
    eco_no: str
    total_items: int
    detected_items: int
    detection_rate: float
    items: List[SummaryItem]


# --- Endpoints ---

@app.get("/api/ecos", response_model=EcoListResponse)
def get_ecos(
    eco_no: Optional[str] = Query(None),
    step_seq: Optional[str] = Query(None),
):
    result = ECO_LIST
    if eco_no:
        result = [e for e in result if eco_no.upper() in e["eco_no"].upper()]
    if step_seq:
        result = [e for e in result if e["step_seq"] == step_seq]

    done_count = sum(1 for e in result if e["status"] == "DONE")
    return {"total": len(result), "done_count": done_count, "items": result}


@app.get("/api/ecos/{eco_no}/summary", response_model=EcoSummary)
def get_eco_summary(eco_no: str):
    return make_summary(eco_no)


@app.get("/api/step-seqs")
def get_step_seqs():
    return STEP_SEQS


@app.get("/api/stats")
def get_stats():
    total = len(ECO_LIST)
    done = sum(1 for e in ECO_LIST if e["status"] == "DONE")
    return {"total_ecos": total, "done_ecos": done, "in_progress": total - done}
