class AnalysesController < ApplicationController
  rescue_from ImageProcessingRunner::Error, with: :render_processing_error

  VALID_CONTENT_TYPES = %w[image/jpeg image/png image/webp image/bmp image/tiff].freeze

  def index
    @analyses = Analysis.recent
  end

  def new
  end

  def show
    @analysis = Analysis.find(params[:id])
    @result = @analysis.result
    render :show
  end

  def create
    upload = params[:image]

    unless valid_upload?(upload)
      flash.now[:alert] = "Envie uma imagem válida nos formatos JPG, PNG, WEBP, BMP ou TIFF."
      render :new, status: :unprocessable_entity
      return
    end

    result = ImageProcessingRunner.call(upload)
    analysis = Analysis.create!(
      result_id: result["result_id"],
      original_filename: upload.original_filename,
      payload: result.except("result_id")
    )

    redirect_to analysis_path(analysis)
  end

  private

  def valid_upload?(upload)
    upload.present? && VALID_CONTENT_TYPES.include?(upload.content_type)
  end

  def render_processing_error(error)
    flash.now[:alert] = error.message
    render :new, status: :unprocessable_entity
  end
end
