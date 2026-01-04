import os
import random
import math
from PIL import Image


def create_classroom_simulation(image_paths, output_path, num_faces, seed=None):
    if seed is not None:
        random.seed(seed)

    CANVAS_WIDTH, CANVAS_HEIGHT = 1920, 1080
    background = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), (240, 240, 240))

    # Selección de imágenes
    if len(image_paths) >= num_faces:
        selected_images = random.sample(image_paths, num_faces)
    else:
        selected_images = random.choices(image_paths, k=num_faces)

    # Configuración dinámica (mantiene tu idea de perspectiva)
    if num_faces > 100:
        MIN_SCALE, MAX_SCALE = 0.14, 0.24
        num_rows = int(math.sqrt(num_faces)) + 2
    elif num_faces > 50:
        MIN_SCALE, MAX_SCALE = 0.16, 0.30
        num_rows = int(math.sqrt(num_faces)) + 1
    else:
        MIN_SCALE, MAX_SCALE = 0.20, 0.40
        num_rows = max(1, int(math.sqrt(num_faces)))

    # Distribución por filas
    rows_data = [[] for _ in range(num_rows)]
    for i, img_path in enumerate(selected_images):
        rows_data[i % num_rows].append(img_path)

    # Arriba/abajo pegado
    TOP_MARGIN = 10
    BOTTOM_MARGIN = 10

    margin_x = 40
    available_width = CANVAS_WIDTH - (2 * margin_x)

    # Evitar solape horizontal
    MIN_GAP_X = 8 if num_faces >= 100 else 6

    # En 100/150/200: NO jitter
    USE_JITTER = (num_faces < 100)

    # -------------------------
    # PASADA 1: plan por fila (sin Y definitivo)
    # -------------------------
    row_plans = []
    used_rows = []

    for r_idx in range(num_rows):
        row_imgs = rows_data[r_idx]
        if not row_imgs:
            row_plans.append({"items": [], "row_h": 0, "scale": 0.0})
            continue

        t = r_idx / (num_rows - 1) if num_rows > 1 else 1.0
        base_scale = MIN_SCALE + (t * (MAX_SCALE - MIN_SCALE))

        dims = []
        for p in row_imgs:
            try:
                with Image.open(p) as im:
                    dims.append((p, im.width, im.height))
            except Exception as e:
                print(f"Skipping {p}: {e}")

        if not dims:
            row_plans.append({"items": [], "row_h": 0, "scale": 0.0})
            continue

        count = len(dims)
        step_x = available_width / (count - 1) if count > 1 else 0

        scale = base_scale
        if count > 1 and step_x > 0:
            max_w = max(w for _, w, _ in dims)
            scale_limit = max(0.01, (step_x - MIN_GAP_X) / max_w)
            scale = min(scale, scale_limit)

        items = []
        max_row_h = 0

        for c_idx, (p, w, h) in enumerate(dims):
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            max_row_h = max(max_row_h, new_h)

            if count > 1:
                center_slot = margin_x + (c_idx * step_x)
            else:
                center_slot = CANVAS_WIDTH / 2

            x_pos = int(center_slot - (new_w / 2))

            items.append({
                "path": p,
                "new_w": new_w,
                "new_h": new_h,
                "x": x_pos,
                "row": r_idx
            })

        row_plans.append({"items": items, "row_h": max_row_h, "scale": scale})

        if items and max_row_h > 0:
            used_rows.append(r_idx)

    if not used_rows:
        raise RuntimeError("No hay imágenes válidas para renderizar.")

    # -------------------------
    # AJUSTE GLOBAL: debe caber en altura sin solape vertical
    # -------------------------
    avail_h = CANVAS_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
    sum_heights = sum(row_plans[r]["row_h"] for r in used_rows)

    global_factor = 1.0
    if sum_heights > avail_h and sum_heights > 0:
        global_factor = avail_h / sum_heights
        for r in used_rows:
            row_plans[r]["row_h"] = max(1, int(row_plans[r]["row_h"] * global_factor))
            for it in row_plans[r]["items"]:
                it["new_w"] = max(1, int(it["new_w"] * global_factor))
                it["new_h"] = max(1, int(it["new_h"] * global_factor))

    sum_heights2 = sum(row_plans[r]["row_h"] for r in used_rows)
    remaining = avail_h - sum_heights2

    gaps = len(used_rows) - 1
    gap_y = max(0, int(remaining / gaps)) if gaps > 0 else 0

    # -------------------------
    # PASADA 2: asignar Y para tocar arriba/abajo sin solape
    # -------------------------
    row_y = {}
    y = TOP_MARGIN
    for i, r in enumerate(used_rows):
        row_y[r] = y
        if i < len(used_rows) - 1:
            y += row_plans[r]["row_h"] + gap_y

    # -------------------------
    # RENDER FINAL
    # -------------------------
    final_items = []
    for r in used_rows:
        for it in row_plans[r]["items"]:
            x = it["x"]
            y = row_y[r]

            if USE_JITTER:
                x += random.randint(-8, 8)
                y += random.randint(-3, 3)

            x = max(0, min(x, CANVAS_WIDTH - it["new_w"]))
            y = max(0, min(y, CANVAS_HEIGHT - it["new_h"]))

            final_items.append({
                "path": it["path"],
                "x": x,
                "y": y,
                "w": it["new_w"],
                "h": it["new_h"],
                "row": r
            })

    final_items.sort(key=lambda d: d["row"])

    for it in final_items:
        try:
            with Image.open(it["path"]) as im:
                im_res = im.resize((it["w"], it["h"]), Image.Resampling.LANCZOS)
                if im_res.mode == "RGBA":
                    background.paste(im_res, (it["x"], it["y"]), im_res)
                else:
                    background.paste(im_res, (it["x"], it["y"]))
        except Exception as e:
            print(f"Skipping render {it['path']}: {e}")

    background.save(output_path)
    print(
        f"Generado: {os.path.abspath(output_path)} "
        f"({num_faces} pax) rows={len(used_rows)} gap_y={gap_y} global_factor={global_factor:.3f}"
    )


if __name__ == "__main__":
    # Dataset relativo al archivo (NO depende del cwd)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "../../datasets/dataset_faces_color"))

    # OUTPUT al MISMO NIVEL que dataset_faces_color
    DATASETS_PARENT = os.path.dirname(BASE_DIR)  # .../datasets
    OUTPUT_DIR = os.path.join(DATASETS_PARENT, "synthetic_classrooms")  # nombre adecuado
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Dataset base:", BASE_DIR)
    print("Output dir  :", OUTPUT_DIR)

    all_images = []
    for i in range(1, 251):
        folder = os.path.join(BASE_DIR, f"s{i}_color")
        p_test = os.path.join(folder, "test.jpg")
        p_front = os.path.join(folder, "front.png")
        if os.path.exists(p_test):
            all_images.append(p_test)
        elif os.path.exists(p_front):
            all_images.append(p_front)

    print(f"Imágenes: {len(all_images)}")
    if not all_images:
        raise RuntimeError("No encontré imágenes. Revisa BASE_DIR y tu estructura de dataset.")

    scenarios = [1, 5, 10, 20, 30, 40, 50, 100, 150, 200]
    for n in scenarios:
        out = os.path.join(OUTPUT_DIR, f"classroom_{n:03d}_faces.jpg")
        create_classroom_simulation(all_images, out, n, seed=42)

    print("--- Finalizado ---")

