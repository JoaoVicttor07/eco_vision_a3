class CreateAnalyses < ActiveRecord::Migration[8.1]
  def change
    create_table :analyses do |t|
      t.string :result_id, null: false
      t.string :original_filename
      t.json :payload, null: false, default: {}

      t.timestamps
    end

    add_index :analyses, :result_id, unique: true
    add_index :analyses, :created_at
  end
end
