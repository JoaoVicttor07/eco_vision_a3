require "json"
require "fileutils"
require "open3"
require "pathname"
require "securerandom"

class ImageProcessingRunner
  class Error < StandardError; end

  MAX_SIZE = 1200

  def self.call(uploaded_file)
    new(uploaded_file).call
  end

  def initialize(uploaded_file)
    @uploaded_file = uploaded_file
  end

  def call
    raise Error, "Selecione uma imagem para processar." if uploaded_file.blank?

    result_id = "#{Time.current.strftime("%Y%m%d%H%M%S")}-#{SecureRandom.hex(4)}"
    output_dir = Rails.root.join("public", "resultados", result_id)
    FileUtils.mkdir_p(output_dir)

    input_path = output_dir.join("input#{safe_extension}")
    File.binwrite(input_path, uploaded_file.read)
    matplotlib_config_dir = Rails.root.join("tmp", "matplotlib")
    FileUtils.mkdir_p(matplotlib_config_dir)

    stdout, stderr, status = Open3.capture3(
      { "MPLCONFIGDIR" => matplotlib_config_dir.to_s },
      python_executable,
      Rails.root.join("script", "process_image.py").to_s,
      "--input", input_path.to_s,
      "--output-dir", output_dir.to_s,
      "--max-size", MAX_SIZE.to_s
    )

    parsed = parse_json(stdout, stderr)
    unless status.success? && parsed["ok"]
      message = parsed["error"].presence || stderr.presence || "Falha ao processar a imagem."
      raise Error, message
    end

    normalize_file_paths(parsed, output_dir)
    parsed.merge("result_id" => result_id)
  end

  private

  attr_reader :uploaded_file

  def safe_extension
    extension = File.extname(uploaded_file.original_filename.to_s).downcase
    return ".png" if extension.blank?

    extension.gsub(/[^a-z0-9.]/, "")
  end

  def python_executable
    return ENV["PYTHON_BIN"] if ENV["PYTHON_BIN"].present?

    local_python = Rails.root.join(".venv", "bin", "python")
    return local_python.to_s if local_python.exist?

    "python3"
  end

  def parse_json(stdout, stderr)
    JSON.parse(stdout)
  rescue JSON::ParserError
    detail = stderr.presence || stdout.presence || "sem saida do processo Python"
    raise Error, "O Python nao retornou um JSON valido: #{detail.to_s.lines.first(4).join.strip}"
  end

  def normalize_file_paths(result, output_dir)
    public_root = Rails.root.join("public").to_s

    result.fetch("files", {}).each do |key, value|
      absolute_path = Pathname.new(value).realpath.to_s
      unless absolute_path.start_with?(public_root)
        raise Error, "Arquivo gerado fora da pasta publica: #{key}"
      end

      result["files"][key] = absolute_path.delete_prefix(public_root)
    end

    result["output_dir"] = output_dir.to_s.delete_prefix(public_root)
  end
end
