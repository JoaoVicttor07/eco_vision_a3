class Analysis < ApplicationRecord
  validates :result_id, presence: true, uniqueness: true

  scope :recent, -> { order(created_at: :desc) }

  def metadata = payload.fetch("metadata", {})
  def metrics = payload.fetch("metrics", {})
  def parameters = payload.fetch("parameters", {})
  def analysis = payload.fetch("analysis", {})
  def files = payload.fetch("files", {})


  def result
    payload.merge("result_id" => result_id)
  end
end
