# app/services/unknown_face_service.py
import requests
import numpy as np
from typing import Optional, List, Tuple, Set

from app.models.unknown_face import UnknownFace
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.course import Course

FACEDETECTION_BASE_URL = "http://127.0.0.1:4000"
DEFAULT_THRESHOLD = 0.3


def _parse_unknown_embedding(embedding_str: str) -> Optional[np.ndarray]:
    if not embedding_str:
        return None
    try:
        arr = np.fromstring(embedding_str, sep=';').astype('float32')
        if arr.size == 0:
            return None
        return arr
    except Exception as e:
        print(f"[ERROR] Failed to parse unknown embedding: {e}")
        return None


def _get_student_embedding(student_id: str) -> Optional[np.ndarray]:
    url = f"{FACEDETECTION_BASE_URL}/student-embedding/{student_id}"
    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as e:
        print(f"[ERROR] Failed to reach facedetection at {url}: {e}")
        return None

    if resp.status_code != 200:
        print(f"[WARN] student-embedding returned {resp.status_code}: {resp.text}")
        return None

    data = resp.json()
    emb_list = data.get("embedding")
    if not emb_list:
        return None

    try:
        emb = np.array(emb_list, dtype='float32')
        if emb.size == 0:
            return None
        return emb
    except Exception as e:
        print(f"[ERROR] Failed to parse student embedding for {student_id}: {e}")
        return None


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a is None or b is None:
        return 0.0

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    a = a / norm_a
    b = b / norm_b
    return float(np.dot(a, b))


def resolve_unknown_faces_for_student(
    student_id: str,
    threshold: Optional[float] = None
) -> Tuple[List[Tuple[UnknownFace, float]], List[Course]]:
    """
    AHORA: solo calcula matches y cursos sugeridos.
    NO modifica UnknownFace.resolved ni UnknownFace.student_id.
    NO hace commit.
    """
    student_id_str = str(student_id)

    # 1. Validar que el student existe
    student = Student.query.get(student_id_str)
    if not student:
        raise ValueError(f"Student with id={student_id_str} not found")

    # 2. Embedding desde facedetection
    stud_emb = _get_student_embedding(student_id_str)
    if stud_emb is None:
        raise RuntimeError(f"No embedding available for student_id={student_id_str}")

    if threshold is None:
        threshold = DEFAULT_THRESHOLD

    # 3. UnknownFaces candidatos (solo no resueltos y sin student_id asignado)
    candidates: List[UnknownFace] = (
        UnknownFace.query
        .filter_by(resolved=False, student_id=None)
        .all()
    )

    print(f"[INFO] Matching unknown faces for student {student_id_str}. Candidates: {len(candidates)}")

    matched: List[Tuple[UnknownFace, float]] = []
    course_ids: Set[str] = set()

    for uf in candidates:
        unk_emb = _parse_unknown_embedding(uf.embedding)
        if unk_emb is None:
            continue

        sim = _cosine_similarity(stud_emb, unk_emb)
        print(f"[DEBUG] UnknownFace id={uf.id} similarity={sim:.4f}")

        if sim >= threshold:
            matched.append((uf, sim))

            if uf.schedule_id:
                sched = Schedule.query.get(uf.schedule_id)
                if sched and sched.course_id:
                    course_ids.add(sched.course_id)

    detected_courses: List[Course] = []
    if course_ids:
        detected_courses = Course.query.filter(Course.id.in_(list(course_ids))).all()

    print(
        f"[INFO] Suggested {len(matched)} matches and {len(detected_courses)} courses "
        f"for student {student_id_str} (no DB changes)."
    )

    return matched, detected_courses
