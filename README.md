# Eco Vision

Pipeline de processamento digital de imagens ambientais em Python. Recebe uma
imagem (foto ou imagem de satélite), executa o pipeline completo de tratamento e
gera os artefatos visuais junto a um relatório de métricas.

O núcleo do sistema é Python e roda de forma totalmente independente. Há também
uma aplicação Ruby on Rails **opcional**, pensada apenas para uma melhor
experiência de visualização (upload pela web e histórico das análises). O
processamento funciona normalmente sem ela.

## O que o pipeline faz

- leitura e conversão BGR -> RGB;
- escala de cinza, redimensionamento e normalização;
- conversão para os espaços de cor HSV e LAB;
- histograma RGB;
- filtros Gaussiano, Mediana e Bilateral;
- detecção de bordas com Canny;
- segmentação por Otsu e morfologia matemática;
- contornos sobrepostos na imagem original;
- análise ambiental: índice de vegetação VARI (NDVI adaptado de RGB) e máscara de
  cobertura vegetal;
- métricas: área segmentada, cobertura vegetal, média de pixels, PSNR e SNR.

## Requisitos

- Python 3.10 ou superior
- OpenCV, NumPy, Matplotlib, Pillow e scikit-image

## Instalação

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Se o `venv` falhar informando que `ensurepip` não está disponível, instale o
pacote `python3-venv` do sistema ou use o bootstrap oficial do pip:

```bash
curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
.venv/bin/python /tmp/get-pip.py
.venv/bin/python -m pip install -r requirements.txt
```

## Como executar

```bash
.venv/bin/python script/process_image.py \
  --input caminho/para/imagem.jpg \
  --output-dir resultados/teste \
  --max-size 1200
```

Parâmetros:

- `--input` — caminho da imagem de entrada (JPG, PNG, etc.).
- `--output-dir` — pasta onde as imagens geradas serão salvas.
- `--max-size` — maior lado da imagem processada, em pixels (padrão 1200).

O script salva os artefatos visuais na pasta de saída e imprime no terminal um
JSON com metadados, métricas, parâmetros e os caminhos dos arquivos gerados.

## Interface web (opcional)

A aplicação Rails apenas embrulha o script Python para oferecer upload e
visualização das análises no navegador. Não é necessária para o processamento.

Requisitos adicionais: Ruby 4.0.2 e Rails 8.1.

```bash
bundle install
bin/rails db:prepare
bin/rails server
```

Acesse `http://localhost:3000`:

- **Início (`/`)** — apresentação e histórico das análises já realizadas.
- **Nova análise (`/analyses/new`)** — envio da imagem.
- **Técnicas (`/tecnicas`)** — explicação de cada método do pipeline.
- **Resultado (`/analyses/:id`)** — detalhe de uma análise.

Cada análise é persistida (metadados/métricas/caminhos) e as imagens geradas
ficam em `public/resultados/<id>`. Por padrão o Rails usa `.venv/bin/python`;
para apontar outro interpretador, defina `PYTHON_BIN`:

```bash
PYTHON_BIN=/caminho/para/python bin/rails server
```

As execuções acumulam pastas em `public/resultados/`. Para remover as antigas:

```bash
bin/rails resultados:limpar             # remove pastas com mais de 7 dias
KEEP_DAYS=1 bin/rails resultados:limpar # ajusta o limite em dias
```
