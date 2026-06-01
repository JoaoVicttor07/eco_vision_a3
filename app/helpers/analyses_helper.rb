module AnalysesHelper
  # Rótulos em português para as chaves de métricas/parâmetros retornadas pelo
  # pipeline Python (que vêm em inglês no JSON). Usado nas tabelas da tela de
  # resultado. Chaves desconhecidas caem no humanize padrão.
  RESULT_LABELS = {
    # Métricas
    "segmented_area_percent" => "Área segmentada (%)",
    "vegetation_cover_percent" => "Cobertura vegetal (%)",
    "mean_pixel_gray" => "Brilho médio (cinza)",
    "mean_pixel_normalized" => "Brilho médio (normalizado)",
    "otsu_threshold" => "Limiar de Otsu",
    "contour_count" => "Número de contornos",
    "psnr_bilateral_gray" => "PSNR (bilateral × cinza)",
    "snr_bilateral_gray" => "SNR (bilateral × cinza)",
    # Parâmetros
    "gaussian_sigma" => "Sigma do Gaussiano",
    "median_kernel" => "Kernel da mediana",
    "bilateral_diameter" => "Diâmetro do bilateral",
    "bilateral_sigma_color" => "Sigma de cor (bilateral)",
    "bilateral_sigma_space" => "Sigma espacial (bilateral)",
    "canny_threshold_low" => "Limiar baixo (Canny)",
    "canny_threshold_high" => "Limiar alto (Canny)",
    "otsu_method" => "Método de Otsu",
    "morphology" => "Morfologia",
    "vegetation_index" => "Índice de vegetação",
    "vegetation_threshold" => "Limiar de vegetação",
    "hsv_green_lower" => "Verde HSV (mínimo)",
    "hsv_green_upper" => "Verde HSV (máximo)"
  }.freeze

  def result_label(key)
    RESULT_LABELS.fetch(key.to_s) { key.to_s.humanize }
  end
end
