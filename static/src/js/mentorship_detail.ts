import 'flowbite';
import htmx from 'htmx.org'
import { Modal } from 'flowbite';
import type { ModalOptions } from 'flowbite';

document.addEventListener("update_mentorship_req_row", (evt) => {
    const row = document.getElementById(evt.detail.row_id)
    if (!row) return
    row.outerHTML = evt.detail.row_html
})

window.getStudentInfo = async (studentUrl:string) => {
    const modalTarget = "#student-info-modal"

    await htmx.ajax("GET", studentUrl, {
        target: `${modalTarget}`,
        swap: "innerHTML",
    })

    const modalElement = document.querySelector(modalTarget) as HTMLElement

    const modalOptions: ModalOptions = {
        closable: true,
        placement: 'bottom-right',
    }
    const modal = new Modal(modalElement,modalOptions);

    // Show the modal after we get its HTML
    modal.show()

    const closeBtn = modalElement.querySelector("#close-btn")
    const requestBtn = modalElement.querySelector("#request-btn")

    // Close the modal when X button is clicked
    closeBtn.addEventListener("click", ()=>{
        modal.hide()
    })

    requestBtn.addEventListener("click", ()=>{
        modal.hide()
    })
}
