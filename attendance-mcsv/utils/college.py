import os
import random
import math
from PIL import Image

def create_classroom_simulation(image_paths, output_name, num_faces):
    CANVAS_WIDTH = 1920
    CANVAS_HEIGHT = 1080
    # Fondo gris claro
    background = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), (240, 240, 240))
    selected_images = []
    while len(selected_images) < num_faces:
        needed = num_faces - len(selected_images)
        pool = list(image_paths)
        random.shuffle(pool)
        selected_images.extend(pool[:needed])
    selected_images = selected_images[:num_faces]
    if num_faces <= 10:
        num_rows = 2
    elif num_faces <= 20:
        num_rows = 3
    elif num_faces <= 30:
        num_rows = 4
    else:
        num_rows = 5
    faces_per_row = math.ceil(num_faces / num_rows)
    min_y = 100
    max_y = 600 
    MIN_SCALE = 0.15 
    MAX_SCALE = 0.35
    rows_data = [[] for _ in range(num_rows)]
    for i, img_path in enumerate(selected_images):
        row_idx = i % num_rows
        rows_data[row_idx].append(img_path)
    final_items = []
    for r_idx in range(num_rows):
        current_row_imgs = rows_data[r_idx]
        count_in_row = len(current_row_imgs)
        if count_in_row == 0: continue
        t = r_idx / (num_rows - 1) if num_rows > 1 else 1.0
        y_pos = int(min_y + (t * (max_y - min_y)))
        scale = MIN_SCALE + (t * (MAX_SCALE - MIN_SCALE))
        margin_x = 100 
        available_width = CANVAS_WIDTH - (2 * margin_x)
        step_x = available_width / count_in_row
        for c_idx, img_path in enumerate(current_row_imgs):
            try:
                img = Image.open(img_path)
                orig_w, orig_h = img.size
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                center_of_slot = margin_x + (c_idx * step_x) + (step_x / 2)
                x_pos = int(center_of_slot - (new_w / 2))
                jitter_range = int(step_x * 0.1)
                x_jitter = random.randint(-jitter_range, jitter_range)
                y_jitter = random.randint(-10, 10)
                final_items.append({
                    'img': img_resized,
                    'x': x_pos + x_jitter,
                    'y': y_pos + y_jitter,
                    'row': r_idx
                })
            except Exception as e:
                print(f"Error procesando {img_path}: {e}")
    final_items.sort(key=lambda item: item['row'])
    for item in final_items:
        if item['img'].mode == 'RGBA':
             background.paste(item['img'], (item['x'], item['y']), item['img'])
        else:
             background.paste(item['img'], (item['x'], item['y']))
    background.save(output_name)
    print(f"Escenario creado: {output_name} ({num_faces} personas)")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    BASE_DIR = os.path.join(project_root, '../datasets/dataset_faces_color')
    print(f"Ruta base: {os.path.abspath(BASE_DIR)}")
    all_images_paths = []
    for i in range(1, 51): 
        folder_path = os.path.join(BASE_DIR, f"s{i}_color")
        path_test = os.path.join(folder_path, "test.jpg") 
        path_front = os.path.join(folder_path, "front.png") 
        if os.path.exists(path_test):
            all_images_paths.append(path_test)
        elif os.path.exists(path_front):
            all_images_paths.append(path_front)
    print(f"Imágenes encontradas: {len(all_images_paths)}")
    if len(all_images_paths) > 0:
        scenarios = [1, 5, 10, 20, 30, 40, 50]
        for n in scenarios:
            output_file = os.path.join(project_root, f"test_scene_{n}_students.jpg")
            create_classroom_simulation(all_images_paths, output_file, n)
        print("\n--- ¡Listo! Imágenes generadas en la raíz del proyecto ---")
    else:
        print("Error: No se encontraron imágenes.")