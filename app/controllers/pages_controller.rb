class PagesController < ApplicationController
  HISTORY_LIMIT = 6

  PIPELINE_PREVIEW = [
    { title: "RGB / HSV / LAB", icon: :palette, anchor: "hsv_lab",
      short: "Conversão entre espaços de cor para realçar atributos específicos." },
    { title: "Histograma", icon: :bar_chart, anchor: "histogram",
      short: "Distribuição de intensidades para avaliar contraste e exposição." },
    { title: "Canny", icon: :scan, anchor: "canny",
      short: "Detecção de bordas multi-estágio com supressão não-máxima." },
    { title: "Otsu", icon: :activity, anchor: "otsu",
      short: "Limiarização automática que maximiza a variância entre classes." },
    { title: "Morfologia", icon: :layers, anchor: "morphology",
      short: "Erosão, dilatação e operações para refinar a segmentação." },
    { title: "VARI", icon: :sprout, anchor: "vegetation",
      short: "Índice de vegetação visível para estimar cobertura vegetal." }
  ].freeze

  def home
    @analyses = Analysis.recent.limit(HISTORY_LIMIT)
    @pipeline_techniques = PIPELINE_PREVIEW
  end

  def techniques
    @techniques = Technique.all
    @categories = Technique.by_category
  end
end
