
# Múltiplo Reconhecimento e Rastreamento de Faces

Este projeto utiliza a biblioteca [face_recognition](https://github.com/ageitgey/face_recognition) para realizar **detecção e reconhecimento** de rostos em tempo real via webcam, além de empregar **trackers** do OpenCV para rastrear as faces entre as detecções.

---

## Sumário

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como Executar](#como-executar)
- [Explicação Geral do Código](#explicação-geral-do-código)
  - [1. Carregamento/Criação do DataFrame de Encodings](#1-carregamentocriação-do-dataframe-de-encodings)
  - [2. Funções Auxiliares (IOU, Contenção, Reconhecimento)](#2-funções-auxiliares-iou-contenção-reconhecimento)
  - [3. Loop Principal (Detecção e Rastreamento)](#3-loop-principal-detecção-e-rastreamento)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Notas Importantes](#notas-importantes)
- [Licença](#licença)

---

## Requisitos

1. **Python 3.7+** (recomendado; testado com Python 3.11).
2. **Bibliotecas** (vide [Instalação](#instalação) para detalhes):
   - `opencv-python` e `opencv-contrib-python` (versão testada: `4.11.0.86`).
   - `numpy`.
   - `cmake` (necessário para compilar algumas dependências do `dlib`, se for instalado via fonte).
   - `dlib` (pode ser instalado via wheel pré-compilado, caso contrário será compilado localmente).
   - `face_recognition`.
   - `tqdm`.
   - `pandas`.

3. **Dependências do Windows** (se estiver em Windows):
   - Microsoft C++ Build Tools (para compilar C/C++ quando necessário).
   - [PowerShell Execution Policy](#instalação) pode precisar ser ajustada, por exemplo:
     ```powershell
     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
     ```
   - Se não usar a wheel pré-compilada para `dlib`, o CMake (3.31.4 ou superior) será necessário para compilar o `dlib`.

---

## Instalação

### 1. Ajuste da Política de Execução (Windows)

Para ativar scripts em PowerShell e permitir a criação de ambientes virtuais sem erro, abra o **PowerShell** como administrador e rode:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
*(Essa etapa pode variar dependendo das configurações de segurança do seu sistema.)*

### 2. Crie e ative um ambiente virtual

```bash
# No Windows:
python -m venv venv
venv\Scripts\activate

# Em Unix (Linux/macOS):
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências na ordem recomendada

Crie ou edite um `requirements.txt` com o seguinte conteúdo, **ajustando o caminho para o wheel do dlib** conforme a localização do seu arquivo:

```text
opencv-python==4.11.0.86
opencv-contrib-python==4.11.0.86
numpy==1.23.5
cmake==3.31.4
# Ajuste abaixo o caminho do seu arquivo .whl do dlib (se você tiver)
dlib @ file:///C:/Users/Windows%2011/Documents/Projects/portifolio/FaceRecognition/dlib-19.24.1-cp311-cp311-win_amd64.whl#sha256=6f1a5ee167975d7952b28e0ce4495f1d9a77644761cf5720fb66d7c6188ae496
face-recognition==1.3.0
tqdm==4.67.1
pandas==2.2.3
```

Então, no seu ambiente virtual ativo, rode:

```bash
pip install -r requirements.txt
```

> **Observação**:  
> - Se você não tiver o wheel do `dlib` pré-compilado, será necessário compilá-lo localmente. Nesse caso, a instalação pode demorar e você precisará ter o **Microsoft Visual C++ Build Tools** e o **CMake** corretamente instalados.

---

## Como Executar

1. **Prepare uma pasta `Data/`** com as imagens de rostos (formato `.jpg`, `.jpeg`, `.png` ou `.bmp`).  
   - Cada arquivo deve conter apenas **um** rosto principal, pois o código pega o primeiro encoding encontrado na imagem.

2. **Execute o script** (por exemplo, `liveFaceBiometry.py` ou outro nome que você tenha dado) no seu terminal com o ambiente virtual ativo:
   ```bash
   python liveFaceBiometry.py
   ```

3. Caso seja a **primeira vez** que você cria o DataFrame de encodings, edite a linha:
   ```python
   CREATE_NEW_DF = True
   ```
   no final do arquivo, dentro da função `main()`. Isso fará com que o sistema crie o arquivo de encodings em `DataBase/encodings.pkl`.

4. Nas **execuções subsequentes**, defina:
   ```python
   CREATE_NEW_DF = False
   ```
   para apenas **carregar** o DF salvo anteriormente, economizando tempo de processamento.

5. O script abrirá uma janela de webcam. A cada *DETECTION_INTERVAL* (30 frames, ~1 segundo) ele fará detecção de novas faces, aplicando *downscale* para agilizar. O nome reconhecido (ou *Unknown*) aparecerá na bounding box do rosto.

6. **Pressione `q`** para encerrar a execução.

---

## Explicação Geral do Código

### 1. Carregamento/Criação do DataFrame de Encodings

A função `load_data_encodings()` faz o seguinte:

- Se `create_df=True`:
  1. Percorre a pasta `Data/`, carrega cada imagem.
  2. Usa `face_recognition` para extrair o **encoding** do primeiro rosto encontrado.
  3. Cria um `DataFrame` com colunas `filename` (nome do arquivo sem extensão) e `encoding`.
  4. Salva esse `DataFrame` em `DataBase/encodings.pkl`.

- Se `create_df=False`:
  1. Simplesmente **carrega** o `DataFrame` de `DataBase/encodings.pkl`, se existir.

Isso evita reprocessar as mesmas imagens toda vez.

### 2. Funções Auxiliares (IOU, Contenção, Reconhecimento)

- `iou(bbox1, bbox2)`: Calcula a **Intersection over Union** para verificar quão sobrepostas duas bounding boxes estão.  
- `is_contained(bbox_small, bbox_large)`: Verifica se uma BB está completamente contida em outra.  
- `recognize_face(face_encoding, df, threshold)`: Faz a comparação do encoding detectado com todos os encodings do `DataFrame`, retornando o nome correspondente se a distância for menor que o threshold, ou `"Unknown"` caso contrário.

### 3. Loop Principal (Detecção e Rastreamento)

1. **Captura de vídeo**: Inicializa `capture = cv2.VideoCapture(0)`.  
2. **Trackers Ativos**: Mantém uma lista `active_trackers`. Cada elemento é um dicionário com:  
   - `tracker`: objeto de rastreamento OpenCV (ex: MOSSE, CSRT etc.).  
   - `face_name`: nome reconhecido ou `"Unknown"`.  
   - `bbox`: bounding box atual `(x, y, w, h)`.

3. **Atualização de Trackers**: Para cada frame, chamamos `tracker.update(frame)`, desenhando bounding box + nome.

4. **Nova Detecção**: A cada `DETECTION_INTERVAL` frames (30 por padrão):
   - Faz *downscale* do frame (redução para 25% do tamanho) para acelerar a detecção.
   - Chama `face_recognition.face_locations(...)`.
   - Ajusta coordenadas para o tamanho original.
   - Remove BBs duplicadas em que uma está contida na outra.
   - Para cada nova BB, checa se já está sendo rastreada (IOU > 0.8 ou contenção). Se não, cria um novo tracker e faz `recognize_face`.

5. **Exibição**: `cv2.imshow("Webcam", frame)` exibe o quadro processado. Tecle `q` para sair.

---

## Estrutura de Pastas

- `Data/`  
  - Pasta com suas imagens de rosto para gerar o encodings.  
- `DataBase/`  
  - Ao criar o DataFrame pela primeira vez, o arquivo `encodings.pkl` será salvo aqui.  
- `liveFaceBiometry.py` (ou outro nome)  
  - Contém o código principal descrito acima.

---

## Notas Importantes

- **Versão do OpenCV**: Se você tiver problemas com `cv2.legacy.TrackerMOSSE_create()`, tente:
  ```python
  tracker = cv2.TrackerMOSSE_create()
  ```
  Ou instale `opencv-contrib-python` mais recente.
  

- **Performance**:  
  1. Ajuste `DETECTION_INTERVAL` (aumente para detectar com menos frequência).  
  2. Use *downscale* (já implementado a 25%).  
  3. Se ainda houver travamentos, considere usar *threading* / *multiprocessing* ou detecção mais leve (ex.: Haar cascades, Mediapipe, etc.).  
  4. Se puder, compile `dlib` com CUDA.

- **Compilação do dlib**:  
  - Se você não tem o wheel pronto, a instalação de `dlib` pode exigir [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) e [cmake](https://cmake.org/).  
  - A instalação pode levar alguns minutos em máquinas Windows.

---

## Licença

Este código é um **exemplo** sem licença definida no repositório, mas sinta-se livre para usá-lo em projetos pessoais ou de pesquisa. Para uso comercial ou redistribuição, verifique as licenças das bibliotecas utilizadas, como `face_recognition`, `OpenCV`, `dlib`, etc.
```