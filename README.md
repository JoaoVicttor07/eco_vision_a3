# Eco Vision A3

Projeto Rails + Python para a Avaliacao A3 de Computacao Grafica. A interface
web recebe uma imagem ambiental enviada pelo usuario e chama um script Python
que executa o pipeline completo de processamento digital de imagens.

## Objetivo

O sistema aplica tecnicas pedidas na proposta do trabalho:

- leitura e conversao BGR -> RGB;
- escala de cinza, redimensionamento e normalizacao;
- conversao para os espacos de cor HSV e LAB;
- histograma RGB;
- filtros Gaussiano, Mediana e Bilateral;
- deteccao de bordas com Canny;
- segmentacao por Otsu;
- morfologia matematica;
- contornos sobrepostos;
- analise ambiental: indice de vegetacao VARI (NDVI adaptado de RGB) e mascara de
  cobertura vegetal;
- analise critica automatica gerada a partir das metricas reais da imagem;
- metricas como area segmentada, cobertura vegetal, media de pixels, PSNR e SNR.

## Dependencias

- Ruby 4.0.2
- Rails 8.1
- Python 3.10 ou superior
- OpenCV, NumPy, Matplotlib, Pillow e scikit-image

Instale as dependencias Python:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Se o comando de `venv` falhar informando que `ensurepip` nao esta disponivel,
instale o pacote `python3-venv` do sistema ou use o bootstrap oficial do pip no
ambiente criado:

```bash
curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
.venv/bin/python /tmp/get-pip.py
.venv/bin/python -m pip install -r requirements.txt
```

Instale as dependencias Ruby:

```bash
bundle install
```

## Como rodar o app

```bash
bin/rails server
```

Acesse `http://localhost:3000`, envie uma imagem ambiental e aguarde o
processamento. Os resultados sao salvos em `public/resultados/<id>`.

Por padrao o Rails tenta usar `.venv/bin/python`. Se quiser apontar para outro
Python, defina:

```bash
PYTHON_BIN=/caminho/para/python bin/rails server
```

## Como rodar apenas o Python

```bash
.venv/bin/python script/process_image.py \
  --input caminho/para/imagem.jpg \
  --output-dir resultados/teste \
  --max-size 1200
```

O script imprime um JSON no terminal com metadados, metricas, parametros e
caminhos dos arquivos gerados.

## Entrega academica

Os entregaveis textuais da proposta A3 tem modelos prontos em `docs/`:

- [`docs/ORIGEM_DA_IMAGEM.md`](docs/ORIGEM_DA_IMAGEM.md) — documente equipamento,
  local, data e como a captura/download foi feito (criterio de 15%). Salve a imagem
  usada como `imagem_original.png` na raiz.
- [`docs/RELATORIO_A3.md`](docs/RELATORIO_A3.md) — base para gerar o `Artigo_a3.pdf`;
  cole as imagens reais de `public/resultados/<id>/` e a tabela de metricas.

## Limpeza dos resultados

As execucoes acumulam pastas em `public/resultados/`. Para podar as antigas:

```bash
bin/rails resultados:limpar            # remove pastas com mais de 7 dias
KEEP_DAYS=1 bin/rails resultados:limpar # ajusta o limite em dias
```

## Testes

```bash
bin/rails test
```
