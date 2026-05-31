namespace :resultados do
  desc "Remove pastas antigas de public/resultados (KEEP_DAYS dias, padrao 7)"
  task limpar: :environment do
    keep_days = Integer(ENV.fetch("KEEP_DAYS", "7"))
    cutoff = keep_days.days.ago
    base_dir = Rails.root.join("public", "resultados")

    removed = 0
    Dir.glob(base_dir.join("*")).each do |path|
      next unless File.directory?(path)
      next if File.mtime(path) >= cutoff

      result_id = File.basename(path)
      FileUtils.rm_rf(path)
      # Mantem banco e disco consistentes: remove o registro da analise podada.
      Analysis.where(result_id: result_id).delete_all
      removed += 1
    end

    puts "Removidas #{removed} pasta(s) de resultados anteriores a #{keep_days} dia(s)."
  end
end
