#!/usr/bin/env python3
"""Pipeline A3 de processamento digital de imagens ambientais.

O script foi pensado para ser consumido pelo Rails via CLI. Ele salva os
artefatos visuais em uma pasta de saida e escreve no stdout um JSON com
metadados, metricas e caminhos dos arquivos gerados.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/eco_vision_matplotlib")

try:
    import cv2
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt
    import numpy as np
except ModuleNotFoundError as error:
    missing_package = error.name or "dependencia"
    payload = {
        "ok": False,
        "error": (
            f"Dependência Python ausente: {missing_package}. "
            "Crie o ambiente com `python3 -m venv .venv` e instale com "
            "`.venv/bin/python -m pip install -r requirements.txt`."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(1)


PARAMETERS = {
    "gaussian_sigma": 1.5,
    "median_kernel": 5,
    "bilateral_diameter": 9,
    "bilateral_sigma_color": 75,
    "bilateral_sigma_space": 75,
    "canny_threshold_low": 50,
    "canny_threshold_high": 150,
    "otsu_method": "THRESH_BINARY + THRESH_OTSU",
    "morphology": "erosão seguida de dilatação, kernel 3x3, 1 iteração",
    "vegetation_index": "VARI = (G - R) / (G + R - B)",
    "vegetation_threshold": 0.05,
    "hsv_green_lower": "(35, 40, 40)",
    "hsv_green_upper": "(85, 255, 255)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Processa uma imagem ambiental para o projeto A3.")
    parser.add_argument("--input", required=True, help="Caminho da imagem original.")
    parser.add_argument("--output-dir", required=True, help="Pasta onde os resultados serao salvos.")
    parser.add_argument("--max-size", type=int, default=1200, help="Maior lado da imagem processada.")
    return parser.parse_args()


def fail(message: str) -> None:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    sys.exit(1)


def web_or_file_path(path: Path) -> str:
    return str(path.resolve())


def save_rgb(path: Path, image_rgb: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), image_bgr)


def save_gray(path: Path, image_gray: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image_gray)


def resize_to_max(image: np.ndarray, max_size: int) -> np.ndarray:
    if max_size <= 0:
        return image

    height, width = image.shape[:2]
    longest_side = max(height, width)
    if longest_side <= max_size:
        return image

    scale = max_size / float(longest_side)
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def plot_histogram(image_rgb: np.ndarray, output_path: Path) -> None:
    colors = {"R": "#d53e4f", "G": "#2ca25f", "B": "#3288bd"}

    plt.figure(figsize=(9, 5))
    for index, (channel, color) in enumerate(colors.items()):
        histogram = cv2.calcHist([image_rgb], [index], None, [256], [0, 256])
        plt.plot(histogram, color=color, label=f"Canal {channel}", linewidth=1.8)

    plt.title("Histograma RGB da imagem original")
    plt.xlabel("Intensidade")
    plt.ylabel("Frequência")
    plt.xlim([0, 255])
    plt.grid(alpha=0.2)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()


def plot_grid(images: list[np.ndarray], titles: list[str], output_path: Path) -> None:
    columns = 3
    rows = math.ceil(len(images) / columns)
    plt.figure(figsize=(14, 4.6 * rows))

    for index, (image, title) in enumerate(zip(images, titles), start=1):
        plt.subplot(rows, columns, index)
        if image.ndim == 2:
            plt.imshow(image, cmap="gray")
        else:
            plt.imshow(image)
        plt.title(title)
        plt.axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()


def save_false_color(path: Path, image_3ch: np.ndarray) -> None:
    """Salva uma representacao em falsa cor de um espaco de cor (HSV/LAB).

    Os tres canais sao gravados diretamente como uma imagem para evidenciar a
    conversao de espaco de cor; nao corresponde a cores reais, e apenas uma
    visualizacao comparativa da transformacao.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image_3ch)


def compute_vegetation(image_rgb: np.ndarray, threshold: float) -> tuple[np.ndarray, np.ndarray, float]:
    """Calcula o indice VARI e a mascara de cobertura vegetal a partir de RGB.

    VARI = (G - R) / (G + R - B). Como fotos RGB nao possuem banda NIR, este e o
    indice de vegetacao adaptado pedido na proposta (NDVI adaptado). Retorna o
    indice (float, [-1, 1]), a mascara binaria de vegetacao e o percentual coberto.
    """
    rgb = image_rgb.astype(np.float32)
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    denominator = green + red - blue
    denominator[np.abs(denominator) < 1e-6] = 1e-6
    vari = (green - red) / denominator
    vari = np.clip(vari, -1.0, 1.0)

    mask = (vari > threshold).astype(np.uint8) * 255
    cover_percent = round(float(np.count_nonzero(mask) / mask.size * 100), 4)
    return vari, mask, cover_percent


def plot_vegetation_index(vari: np.ndarray, output_path: Path) -> None:
    plt.figure(figsize=(8, 6))
    image = plt.imshow(vari, cmap="RdYlGn", vmin=-1.0, vmax=1.0)
    plt.title("Índice de vegetação (VARI)")
    plt.axis("off")
    colorbar = plt.colorbar(image, fraction=0.046, pad=0.04)
    colorbar.set_label("VARI (verde = vegetação)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()


def build_analysis(metrics: dict[str, Any], channel_means: dict[str, float]) -> dict[str, str]:
    """Gera frases de analise critica a partir das metricas reais da imagem."""
    dominant_channel = max(channel_means, key=channel_means.get)
    channel_label = {"R": "vermelho", "G": "verde", "B": "azul"}[dominant_channel]
    channel_hint = {
        "R": "tons quentes (solo exposto, construções ou áreas degradadas)",
        "G": "predominância de vegetação saudável",
        "B": "presença de água ou céu na cena",
    }[dominant_channel]

    area = metrics["segmented_area_percent"]
    if area < 15:
        area_reading = "poucas regiões destacadas pela limiarização"
    elif area < 50:
        area_reading = "regiões de interesse moderadas separadas do fundo"
    else:
        area_reading = "grande parte da cena classificada como região de interesse"

    cover = metrics["vegetation_cover_percent"]
    if cover < 10:
        cover_reading = "cobertura vegetal baixa, indicando área pouco verde ou degradada"
    elif cover < 40:
        cover_reading = "cobertura vegetal parcial, com mistura de vegetação e outras superfícies"
    else:
        cover_reading = "cobertura vegetal alta, compatível com área densamente vegetada"

    return {
        "original": (
            f"Canal dominante: {channel_label} (média {channel_means[dominant_channel]:.1f}), "
            f"sugerindo {channel_hint}."
        ),
        "histogram": (
            f"Médias por canal R={channel_means['R']:.1f}, G={channel_means['G']:.1f}, "
            f"B={channel_means['B']:.1f}. O canal {channel_label} concentra mais energia, "
            "coerente com a distribuição observada no histograma."
        ),
        "segmentation": (
            f"O limiar de Otsu ({metrics['otsu_threshold']:.0f}) gerou {area_reading} "
            f"({area:.1f}% da área), com {metrics['contour_count']} contornos após a morfologia."
        ),
        "vegetation": (
            f"O índice VARI estima {cover:.1f}% de cobertura vegetal: {cover_reading}."
        ),
        "overall": (
            f"A cena apresenta {channel_hint}; a limiarização destacou {area:.1f}% de regiões "
            f"de interesse e o índice de vegetação apontou {cover:.1f}% de área verde. "
            f"PSNR de {metrics.get('psnr_bilateral_gray')} dB entre a imagem em cinza e a "
            "versão filtrada por bilateral indica o grau de suavização aplicado preservando bordas."
        ),
    }


def calculate_psnr(reference_gray: np.ndarray, processed_gray: np.ndarray) -> float | None:
    mse = np.mean((reference_gray.astype(np.float64) - processed_gray.astype(np.float64)) ** 2)
    if mse == 0:
        return None
    return round(float(20 * math.log10(255.0 / math.sqrt(mse))), 4)


def calculate_snr(reference_gray: np.ndarray, processed_gray: np.ndarray) -> float | None:
    signal = np.mean(reference_gray.astype(np.float64) ** 2)
    noise = np.mean((reference_gray.astype(np.float64) - processed_gray.astype(np.float64)) ** 2)
    if noise == 0:
        return None
    return round(float(10 * math.log10(signal / noise)), 4)


def process_image(input_path: Path, output_dir: Path, max_size: int) -> dict[str, Any]:
    if not input_path.exists():
        fail(f"Arquivo não encontrado: {input_path}")

    image_bgr = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        fail("Não foi possível ler a imagem. Envie um arquivo JPG, PNG ou outro formato suportado pelo OpenCV.")

    output_dir.mkdir(parents=True, exist_ok=True)

    original_size_kb = round(input_path.stat().st_size / 1024, 2)
    original_height, original_width = image_bgr.shape[:2]
    channels = image_bgr.shape[2] if image_bgr.ndim == 3 else 1

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_rgb = resize_to_max(image_rgb, max_size=max_size)
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    normalized = gray.astype(np.float32) / 255.0

    hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
    vari, vegetation_mask, vegetation_cover_percent = compute_vegetation(
        image_rgb, PARAMETERS["vegetation_threshold"]
    )

    gaussian = cv2.GaussianBlur(image_rgb, (0, 0), PARAMETERS["gaussian_sigma"])
    median = cv2.medianBlur(image_rgb, PARAMETERS["median_kernel"])
    bilateral = cv2.bilateralFilter(
        image_rgb,
        PARAMETERS["bilateral_diameter"],
        PARAMETERS["bilateral_sigma_color"],
        PARAMETERS["bilateral_sigma_space"],
    )

    edges = cv2.Canny(gray, PARAMETERS["canny_threshold_low"], PARAMETERS["canny_threshold_high"])
    otsu_threshold, otsu_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    morph_mask = cv2.dilate(cv2.erode(otsu_mask, kernel, iterations=1), kernel, iterations=1)

    contours, _ = cv2.findContours(morph_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_overlay_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    cv2.drawContours(contour_overlay_bgr, contours, -1, (30, 220, 40), 2)
    contour_overlay = cv2.cvtColor(contour_overlay_bgr, cv2.COLOR_BGR2RGB)

    paths = {
        "original": output_dir / "original.png",
        "gray": output_dir / "gray.png",
        "gaussian": output_dir / "gaussian.png",
        "median": output_dir / "median.png",
        "bilateral": output_dir / "bilateral.png",
        "edges": output_dir / "edges_canny.png",
        "otsu_mask": output_dir / "otsu_mask.png",
        "morphology_mask": output_dir / "morphology_mask.png",
        "contours": output_dir / "contours.png",
        "histogram": output_dir / "histogram_rgb.png",
        "hsv": output_dir / "hsv.png",
        "lab": output_dir / "lab.png",
        "vegetation_index": output_dir / "vegetation_index.png",
        "vegetation_mask": output_dir / "vegetation_mask.png",
        "grid": output_dir / "comparison_grid.png",
    }

    save_rgb(paths["original"], image_rgb)
    save_gray(paths["gray"], gray)
    save_rgb(paths["gaussian"], gaussian)
    save_rgb(paths["median"], median)
    save_rgb(paths["bilateral"], bilateral)
    save_gray(paths["edges"], edges)
    save_gray(paths["otsu_mask"], otsu_mask)
    save_gray(paths["morphology_mask"], morph_mask)
    save_rgb(paths["contours"], contour_overlay)
    save_false_color(paths["hsv"], hsv)
    save_false_color(paths["lab"], lab)
    save_gray(paths["vegetation_mask"], vegetation_mask)
    plot_histogram(image_rgb, paths["histogram"])
    plot_vegetation_index(vari, paths["vegetation_index"])
    plot_grid(
        [
            image_rgb,
            gray,
            gaussian,
            median,
            bilateral,
            edges,
            otsu_mask,
            morph_mask,
            contour_overlay,
            vari,
            vegetation_mask,
        ],
        [
            "Original",
            "Escala de cinza",
            "Filtro Gaussiano",
            "Filtro de Mediana",
            "Filtro Bilateral",
            "Bordas Canny",
            "Mascara Otsu",
            "Morfologia",
            "Contornos",
            "Indice VARI",
            "Mascara de vegetacao",
        ],
        paths["grid"],
    )

    processed_gray = cv2.cvtColor(bilateral, cv2.COLOR_RGB2GRAY)
    segmented_area_percent = round(float(np.count_nonzero(morph_mask) / morph_mask.size * 100), 4)
    channel_means = {
        "R": float(np.mean(image_rgb[:, :, 0])),
        "G": float(np.mean(image_rgb[:, :, 1])),
        "B": float(np.mean(image_rgb[:, :, 2])),
    }

    metrics = {
        "segmented_area_percent": segmented_area_percent,
        "vegetation_cover_percent": vegetation_cover_percent,
        "mean_pixel_gray": round(float(np.mean(gray)), 4),
        "mean_pixel_normalized": round(float(np.mean(normalized)), 4),
        "otsu_threshold": round(float(otsu_threshold), 4),
        "contour_count": len(contours),
        "psnr_bilateral_gray": calculate_psnr(gray, processed_gray),
        "snr_bilateral_gray": calculate_snr(gray, processed_gray),
    }

    return {
        "ok": True,
        "metadata": {
            "original_width": original_width,
            "original_height": original_height,
            "processed_width": int(image_rgb.shape[1]),
            "processed_height": int(image_rgb.shape[0]),
            "channels": channels,
            "size_kb": original_size_kb,
        },
        "metrics": metrics,
        "analysis": build_analysis(metrics, channel_means),
        "parameters": PARAMETERS,
        "files": {key: web_or_file_path(value) for key, value in paths.items()},
    }


def main() -> None:
    args = parse_args()
    result = process_image(Path(args.input), Path(args.output_dir), args.max_size)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
