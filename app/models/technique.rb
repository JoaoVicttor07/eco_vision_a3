class Technique
  CONFIG_PATH = Rails.root.join("config", "techniques.yml")

  attr_reader :key, :name, :category, :what, :how, :goal, :interpret, :params

  def initialize(key, attrs)
    @key = key
    @name = attrs["name"]
    @category = attrs["category"]
    @what = attrs["what"]
    @how = attrs["how"]
    @goal = attrs["goal"]
    @interpret = attrs["interpret"]
    @params = attrs["params"]
  end

  def self.all
    @all ||= load_config.map { |key, attrs| new(key, attrs) }
  end

  def self.by_category
    all.group_by(&:category)
  end

  def self.find(key)
    all.find { |technique| technique.key == key.to_s }
  end

  def self.load_config
    config = YAML.load_file(CONFIG_PATH)
    config.is_a?(Hash) ? config : {}
  end

  def self.reload!
    @all = nil
  end
end
