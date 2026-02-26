"""
RAG Service — Medical knowledge retrieval using ChromaDB.
Loads curated medical text, chunks it, embeds it, and retrieves relevant context for report generation.
"""
import os
from pathlib import Path
from app.config import settings
from app.core.logging import logger

_collection = None
_client = None


def _get_knowledge_dir() -> Path:
    return Path(__file__).parent / "rag_knowledge"


def _get_knowledge_texts() -> dict[str, str]:
    """Load all knowledge text files. If files don't exist, use built-in knowledge."""
    knowledge_dir = _get_knowledge_dir()
    texts = {}

    if knowledge_dir.exists():
        for f in knowledge_dir.glob("*.txt"):
            texts[f.stem] = f.read_text(encoding="utf-8")

    # Fallback built-in knowledge if no files exist
    if not texts:
        texts = _builtin_knowledge()

    return texts


def _builtin_knowledge() -> dict[str, str]:
    return {
        "lung_cancer": """
Lung cancer staging follows TNM classification. Stage I: tumor confined to lung, no lymph node involvement.
Stage II: tumor with ipsilateral peribronchial/hilar lymph node involvement. Stage III: locally advanced disease.
Stage IV: metastatic disease. Risk factors: smoking (pack-years), radon exposure, asbestos, family history.
LungRADS categories: 1 (negative), 2 (benign), 3 (probably benign), 4A (suspicious), 4B (very suspicious).
Nodule characteristics: spiculated margins suggest malignancy. Ground-glass opacity may indicate adenocarcinoma.
Solid nodules >8mm require follow-up. Volume doubling time <400 days suggests malignancy.
Treatment: Stage I-II surgical resection (lobectomy). Stage III chemoradiation. Stage IV systemic therapy.
EGFR mutations, ALK rearrangements, PD-L1 expression guide targeted therapy selection.
Screening recommended for adults 50-80 with 20+ pack-year history. Low-dose CT annually.
5-year survival: Stage I 68-92%, Stage II 53-60%, Stage III 13-36%, Stage IV 0-10%.
""",
        "blood_cancer": """
Leukemia classification: Acute Lymphoblastic (ALL), Acute Myeloid (AML), Chronic Lymphocytic (CLL), Chronic Myeloid (CML).
CBC biomarkers: WBC >11,000 elevated, blast percentage >5% abnormal in peripheral blood, >20% diagnostic for acute leukemia.
Hemoglobin <12 g/dL (women) or <13.5 g/dL (men) indicates anemia. Platelets <150,000 indicates thrombocytopenia.
Peripheral blood smear findings: blast cells, Auer rods (AML), smudge cells (CLL).
Flow cytometry markers: CD19, CD20 (B-cell), CD3, CD5 (T-cell), CD34, CD117 (stem cell).
Treatment: ALL - multi-agent chemotherapy, CNS prophylaxis. AML - 7+3 induction. CML - TKI (imatinib).
Risk stratification: cytogenetics (favorable: t(8;21), inv(16); adverse: complex karyotype, -7).
Minimal residual disease (MRD) assessment guides treatment decisions.
""",
        "brain_tumor": """
Brain tumor WHO grading: Grade I (pilocytic astrocytoma) - benign, Grade II (diffuse astrocytoma) - low-grade,
Grade III (anaplastic astrocytoma) - high-grade, Grade IV (glioblastoma) - most aggressive.
MRI findings: T1-weighted shows anatomy, T2/FLAIR shows edema, contrast enhancement suggests high-grade.
Meningiomas: extra-axial, dural-based, homogeneous enhancement. Usually WHO Grade I.
Pituitary adenomas: sellar/suprasellar mass, may cause visual field defects. Microadenoma <10mm.
Glioblastoma: ring-enhancing lesion with central necrosis, surrounding edema. Median survival 15 months.
IDH mutation status: IDH-mutant has better prognosis. MGMT methylation predicts temozolomide response.
Treatment: maximal safe resection + radiation + temozolomide (Stupp protocol for GBM).
Molecular markers: 1p/19q codeletion (oligodendroglioma), BRAF V600E (pleomorphic xanthoastrocytoma).
""",
        "ct_findings": """
CT scan nodule classification: solid, part-solid, ground-glass. Size measurement on lung window.
Hounsfield units (HU): air -1000, fat -100, water 0, blood 30-45, muscle 40-60, bone 400-1000.
Lung window: W1200/L-600. Mediastinal window: W400/L40. Bone window: W1800/L400.
Pulmonary nodule characteristics suggesting malignancy: spiculated margins, upper lobe location,
size >8mm, growth on serial imaging, associated lymphadenopathy.
Fleischner Society guidelines for incidental pulmonary nodules management.
Ground-glass nodules: may represent atypical adenomatous hyperplasia, adenocarcinoma in situ.
RECIST criteria: Complete Response (CR), Partial Response (PR), Stable Disease (SD), Progressive Disease (PD).
""",
        "general_oncology": """
Cancer screening guidelines: lung (LDCT), breast (mammography), cervical (Pap/HPV), colorectal (colonoscopy).
TNM staging: T (tumor size/extent), N (lymph node involvement), M (distant metastasis).
ECOG Performance Status: 0 (fully active) to 4 (completely disabled).
Cancer biomarkers: CEA (colorectal), CA-125 (ovarian), PSA (prostate), AFP (liver), CA 19-9 (pancreatic).
Immunotherapy checkpoint inhibitors: anti-PD-1 (pembrolizumab, nivolumab), anti-PD-L1 (atezolizumab).
Clinical trial phases: Phase I (safety), Phase II (efficacy), Phase III (comparative), Phase IV (post-market).
RECIST 1.1 criteria for tumor response assessment. iRECIST for immunotherapy response.
AI in oncology: computer-aided detection (CADe), computer-aided diagnosis (CADx).
Sensitivity and specificity thresholds for clinical deployment. AUC-ROC > 0.95 considered excellent.
""",
    }


def initialize():
    """Initialize the ChromaDB collection with medical knowledge."""
    global _collection, _client
    try:
        import chromadb
        _client = chromadb.Client()  # In-memory for simplicity
        _collection = _client.get_or_create_collection(
            name="medical_knowledge",
            metadata={"hnsw:space": "cosine"},
        )

        # Check if already populated
        if _collection.count() > 0:
            logger.info(f"RAG collection already has {_collection.count()} documents.")
            return

        texts = _get_knowledge_texts()
        documents = []
        ids = []
        metadatas = []

        for topic, content in texts.items():
            # Simple chunking by paragraphs/sentences
            chunks = [c.strip() for c in content.split("\n") if c.strip() and len(c.strip()) > 20]
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"{topic}_{i}")
                metadatas.append({"topic": topic})

        if documents:
            _collection.add(documents=documents, ids=ids, metadatas=metadatas)
            logger.info(f"RAG initialized with {len(documents)} chunks from {len(texts)} topics.")

    except ImportError:
        logger.warning("ChromaDB not installed. RAG will use fallback context.")
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}. Using fallback.")


def retrieve_context(cancer_type: str, predicted_class: str, confidence: float, n_results: int = 5) -> list[str]:
    """
    Retrieve relevant medical context for a given prediction.
    Returns list of relevant text passages.
    """
    if _collection is None or _collection.count() == 0:
        return _fallback_context(cancer_type, predicted_class)

    query = f"{cancer_type} cancer {predicted_class} diagnosis confidence {confidence}%"
    try:
        results = _collection.query(query_texts=[query], n_results=n_results)
        if results and results["documents"]:
            return results["documents"][0]
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")

    return _fallback_context(cancer_type, predicted_class)


def _fallback_context(cancer_type: str, predicted_class: str) -> list[str]:
    """Return basic context when RAG isn't available."""
    knowledge = _builtin_knowledge()
    topic_key = cancer_type.lower().replace(" ", "_")

    # Find matching topic
    for key, text in knowledge.items():
        if topic_key in key or cancer_type.lower() in key:
            chunks = [c.strip() for c in text.split("\n") if c.strip() and len(c.strip()) > 20]
            return chunks[:5]

    return [f"Analysis for {cancer_type}: {predicted_class} detected."]
