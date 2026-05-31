import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["modal", "image"]

  open(event) {
    const img = event.target.closest("img")
    if (!img) return
    if (this.hasModalTarget && this.modalTarget.contains(img)) return

    this.imageTarget.src = img.currentSrc || img.src
    this.imageTarget.alt = img.alt || ""
    this.modalTarget.classList.add("is-open")
    document.body.classList.add("modal-open")
  }

  close() {
    this.modalTarget.classList.remove("is-open")
    document.body.classList.remove("modal-open")
    this.imageTarget.removeAttribute("src")
  }

  backdrop(event) {
    if (event.target === event.currentTarget) this.close()
  }

  closeOnEsc(event) {
    if (event.key === "Escape" && this.modalTarget.classList.contains("is-open")) {
      this.close()
    }
  }
}
