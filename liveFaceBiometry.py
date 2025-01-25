import os
import cv2
import numpy as np
import pandas as pd
import face_recognition
from tqdm import tqdm
import pickle

# -------------------------------
# Funções Auxiliares
# -------------------------------
def iou(bbox1, bbox2):
    """
    Calcula a Intersection over Union (IOU) entre duas bounding boxes.
    bbox no formato (x, y, w, h) -- canto superior esquerdo (x, y) + largura e altura.
    """
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2

    # Coordenadas dos cantos sup. esquerdo e inf. direito
    sx1, sy1, ex1, ey1 = x1, y1, x1 + w1, y1 + h1
    sx2, sy2, ex2, ey2 = x2, y2, x2 + w2, y2 + h2

    # Área de cada bbox
    area1 = w1 * h1
    area2 = w2 * h2

    # Interseção
    inter_x1 = max(sx1, sx2)
    inter_y1 = max(sy1, sy2)
    inter_x2 = min(ex1, ex2)
    inter_y2 = min(ey1, ey2)

    if inter_x2 < inter_x1 or inter_y2 < inter_y1:
        # Sem interseção
        return 0.0

    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    # IOU
    return inter_area / float(area1 + area2 - inter_area)


def is_contained(bbox_small, bbox_large):
    """
    Verifica se bbox_small está completamente contida em bbox_large.
    Formato (x, y, w, h).
    """
    xA, yA, wA, hA = bbox_small
    xB, yB, wB, hB = bbox_large

    # Canto inferior direito
    xA2 = xA + wA
    yA2 = yA + hA
    xB2 = xB + wB
    yB2 = yB + hB

    # Verifica se (xA, yA) >= (xB, yB) e (xA2, yA2) <= (xB2, yB2)
    return (xA >= xB) and (yA >= yB) and (xA2 <= xB2) and (yA2 <= yB2)


def load_data_encodings(folder_path="Images", create_df=True):
    """
    Se create_df=True:
        - Lê as imagens da pasta 'folder_path';
        - Extrai o encoding (caso exista rosto);
        - Cria um DataFrame pandas com:
            * 'filename' (sem extensão)
            * 'encoding'
        - Cria (se não existir) a pasta 'DataBase'
        - Salva o DataFrame em 'DataBase/encodings.pkl'

    Se create_df=False:
        - Tenta carregar o DataFrame em 'DataBase/encodings.pkl'
        - Se não existir, lança exceção.
    """
    db_path = "DataBase"
    pkl_path = os.path.join(db_path, "encodings.pkl")

    if not create_df:
        # Tentar carregar
        if os.path.exists(pkl_path):
            with open(pkl_path, "rb") as f:
                df = pickle.load(f)
            print("[INFO] DataFrame carregado de:", pkl_path)
            return df
        else:
            raise FileNotFoundError(
                f"Não foi encontrado {pkl_path} para carregar. "
                "Defina create_df=True para criar."
            )

    # Se create_df=True, construir o DF do zero
    print("[INFO] Criando novo DataFrame de encodings...")

    data = []
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp")

    if not os.path.exists(folder_path):
        raise ValueError(f"A pasta {folder_path} não existe.")

    for filename in tqdm(os.listdir(folder_path)):
        if filename.lower().endswith(valid_extensions):
            file_path = os.path.join(folder_path, filename)
            # Remove a extensão do arquivo ("me.jpg" -> "me")
            filename_no_ext = os.path.splitext(filename)[0]

            # Carrega a imagem
            image = face_recognition.load_image_file(file_path)
            # Extrai encodings
            encodings = face_recognition.face_encodings(image)
            # Se encontrar ao menos um rosto, pega o primeiro encoding
            if len(encodings) > 0:
                encoding = encodings[0]
                data.append([filename_no_ext, encoding])

    df = pd.DataFrame(data, columns=["filename", "encoding"])

    # Se a pasta DataBase não existe, criar
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    # Salvar o DF em pickle
    with open(pkl_path, "wb") as f:
        pickle.dump(df, f)

    print("[INFO] DataFrame criado e salvo em:", pkl_path)
    return df


def recognize_face(face_encoding, df, threshold=0.6):
    """
    Compara o encoding 'face_encoding' com todos os encodings
    contidos no DataFrame 'df' (coluna 'encoding').
    Retorna o 'filename' da face mais similar se a distância
    mínima for menor que 'threshold'. Caso contrário, 'Unknown'.
    """
    known_encodings = df["encoding"].tolist()
    distances = face_recognition.face_distance(known_encodings, face_encoding)
    min_distance_index = np.argmin(distances)
    if distances[min_distance_index] < threshold:
        return df.loc[min_distance_index, "filename"]
    else:
        return "Unknown"


def main():
    CREATE_NEW_DF = True  # True -> recria DF / False -> carrega DF existente
    df_encodings = load_data_encodings(folder_path="Images", create_df=CREATE_NEW_DF)

    capture = cv2.VideoCapture(0)

    # Lista de 'rastreamento' para múltiplas faces
    # Cada item será um dicionário: { 'tracker': ..., 'face_name': ..., 'bbox': (x, y, w, h) }
    active_trackers = []

    # Parâmetros
    threshold = 0.6
    bb_color = (0, 255, 0)  # cor do retângulo (verde)

    frame_count = 0
    DETECTION_INTERVAL = 30  # detecta a cada 30 frames
    IOU_THRESHOLD = 0.8      # se IOU > 0.8, consideramos a face "igual" a uma rastreada

    while True:
        ret, frame = capture.read()
        if not ret:
            print("[ERRO] Não foi possível ler o frame da câmera.")
            break

        frame_count += 1

        # ------------------------------
        # (1) Atualiza cada tracker existente e desenha
        # ------------------------------
        removed_trackers = []
        for i, tracker_info in enumerate(active_trackers):
            tracker = tracker_info["tracker"]
            face_name = tracker_info["face_name"]

            success, box = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in box]
                # Atualiza a bbox
                tracker_info["bbox"] = (x, y, w, h)

                # Desenha retângulo e nome
                cv2.rectangle(frame, (x, y), (x + w, y + h), bb_color, 2)
                cv2.rectangle(frame, (x, y + h - 25), (x + w, y + h), bb_color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, face_name, (x + 4, y + h - 6), font, 0.6, (0, 0, 255), 1)
            else:
                removed_trackers.append(i)

        # Remove trackers que falharam
        for i in reversed(removed_trackers):
            del active_trackers[i]

        # ------------------------------
        # (2) A cada DETECTION_INTERVAL frames, faz detecção de novas faces
        # ------------------------------
        if frame_count % DETECTION_INTERVAL == 0:
            # a) Downscale
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # b) Detecta faces (em RGB se quiser mais precisão)
            #    aqui estamos usando BGR direto, mas face_recognition recomenda RGB
            face_locations_small = face_recognition.face_locations(small_frame)

            # c) Ajusta coordenadas para o frame original
            detection_bboxes = []
            for (top_s, right_s, bottom_s, left_s) in face_locations_small:
                # Reescala para as dimensões originais
                top = top_s * 4
                right = right_s * 4
                bottom = bottom_s * 4
                left = left_s * 4

                w = right - left
                h = bottom - top
                detection_bboxes.append((left, top, w, h))  # formato (x, y, w, h)

            # d) Filtra BBs que estão contidas dentro de outras
            final_bboxes = []
            for i, bb1 in enumerate(detection_bboxes):
                contained_in_another = False
                for j, bb2 in enumerate(detection_bboxes):
                    if i == j:
                        continue
                    # Se bb1 está contida em bb2, ignorar bb1
                    if is_contained(bb1, bb2):
                        contained_in_another = True
                        break
                if not contained_in_another:
                    final_bboxes.append(bb1)

            # e) Para cada bbox final, verifica IOU / containment com trackers existentes
            for new_bbox in final_bboxes:
                x, y, w, h = new_bbox
                already_tracked = False

                # Verifica se coincide com alguma bbox rastreada
                for tracker_info in active_trackers:
                    tracked_bbox = tracker_info["bbox"]
                    # Checa IOU
                    if iou(tracked_bbox, new_bbox) > IOU_THRESHOLD:
                        already_tracked = True
                        break
                    # Ou se new_bbox está contida na tracked_bbox (opcional)
                    if is_contained(new_bbox, tracked_bbox):
                        already_tracked = True
                        break
                    # (poderia também checar se tracked_bbox está contida em new_bbox)

                # Se não coincide, criamos um tracker novo
                if not already_tracked:
                    # Extrai encoding
                    # Precisamos das coords top, right, bottom, left
                    top = y
                    left = x
                    right = x + w
                    bottom = y + h

                    face_enc = face_recognition.face_encodings(frame, [(top, right, bottom, left)])
                    if len(face_enc) > 0:
                        face_encoding = face_enc[0]
                        face_name = recognize_face(face_encoding, df_encodings, threshold)
                    else:
                        face_name = "Unknown"

                    # Cria tracker
                    new_tracker = cv2.legacy.TrackerMOSSE_create()
                    new_tracker.init(frame, (x, y, w, h))

                    active_trackers.append({
                        "tracker": new_tracker,
                        "face_name": face_name,
                        "bbox": (x, y, w, h)
                    })

        # ------------------------------
        # (3) Exibe o frame
        # ------------------------------
        cv2.imshow("Webcam", frame)

        # Tecla 'q' para sair
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
