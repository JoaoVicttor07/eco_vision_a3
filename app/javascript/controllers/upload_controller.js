import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "filename", "preview", "dropzone", "button"]

  select() {
    const file = this.inputTarget.files[0]

    if (!file) {
      this.reset()
      return
    }

    this.filenameTarget.textContent = file.name
    this.dropzoneTarget.classList.add("has-file")

    if (file.type.startsWith("image/")) {
      this.previewTarget.src = URL.createObjectURL(file)
      this.previewTarget.classList.add("is-visible")
    }
  }

  submit() {
    this.buttonTarget.value = "Processando..."
    this.buttonTarget.disabled = true
    this.element.classList.add("is-processing")
  }

  reset() {
    this.filenameTarget.textContent = "JPG, PNG, WEBP, BMP ou TIFF"
    this.previewTarget.removeAttribute("src")
    this.previewTarget.classList.remove("is-visible")
    this.dropzoneTarget.classList.remove("has-file")
  }
}
